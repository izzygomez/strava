import traceback
from datetime import datetime, timedelta

import pytz

from services import google_calendar_api, ntfy_api, strava_api
from utils import cli_args, time_utils
from utils.load_env import (
    GOOGLE_CALENDAR_STRAVA_CALENDAR_ID,
    NTFY_TOPIC_URL,
    STRAVA_CLIENT_ID,
    STRAVA_CLIENT_SECRET,
    STRAVA_REFRESH_TOKEN,
)

UTC = pytz.timezone("UTC")
UTC_STR = UTC.zone


def _build_event(activity, start_time, end_time) -> dict:
    """
    Build a Google Calendar event object from a Strava activity object.
    """
    emoji = strava_api.get_emoji_for_sport_type(activity["sport_type"])
    event_title = f"{emoji} • {activity['name']}"
    event_description = strava_api.get_activity_url(activity["id"])
    return {
        "summary": event_title,
        "description": event_description,
        "start": {
            "dateTime": start_time,
            "timeZone": UTC_STR,
        },
        "end": {
            "dateTime": end_time,
            "timeZone": UTC_STR,
        },
    }


def _compare_events(local_event, gcal_event) -> list:
    """
    Compare two event objects and return a list of fields that differ.

    Note that I'm comparing fields manually because of some required custom
    handling - if fields are added in _build_event(), they should be added here.
    """
    diff = []

    if local_event["summary"] != gcal_event["summary"]:
        diff.append("summary")
    if local_event["description"] != gcal_event["description"]:
        diff.append("description")

    # custom handling for start & end to gracefully handle datetime equalities
    local_start_datetime = datetime.fromisoformat(local_event["start"]["dateTime"])
    gcal_start_datetime = datetime.fromisoformat(gcal_event["start"]["dateTime"])
    if (
        local_start_datetime != gcal_start_datetime
        or local_event["start"]["timeZone"] != gcal_event["start"]["timeZone"]
    ):
        diff.append("start")

    local_end_datetime = datetime.fromisoformat(local_event["end"]["dateTime"])
    gcal_end_datetime = datetime.fromisoformat(gcal_event["end"]["dateTime"])
    if (
        local_end_datetime != gcal_end_datetime
        or local_event["end"]["timeZone"] != gcal_event["end"]["timeZone"]
    ):
        diff.append("end")

    return diff


def strava_to_gcal(
    start_date: datetime,
    end_date: datetime,
    dry_run: bool = False,
    force_refresh: bool = False,
) -> dict:
    service = google_calendar_api.create_google_calendar_service()
    if not service:
        print("Failed to get Google Calendar service.")
        raise

    mode = "[DRY RUN] " if dry_run else ""
    print(f"📅 {mode}Syncing Strava activities to Google Calendar...")
    strava_access_token = strava_api.get_strava_access_token(
        STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
    )
    print()
    all_activities = strava_api.get_sorted_strava_activities(
        strava_access_token, start_date, end_date, force_refresh=force_refresh
    )

    print()
    print(f"{mode}Creating/Updating Google Calendar events for Strava activities...")
    created_events = 0
    updated_events = 0
    non_modified_events = 0
    for i, activity in enumerate(all_activities):
        print_count = 50
        if (i + 1) % print_count == 0:
            print()
            print(f"Processing activity {i + 1}/{len(all_activities)}...")

        # Normalize start & end times to UTC for Google Calendar API
        start_time = datetime.fromisoformat(activity["start_date"])
        end_time = start_time + timedelta(seconds=activity["elapsed_time"])
        start_time = start_time.astimezone(UTC).isoformat()
        end_time = end_time.astimezone(UTC).isoformat()

        # Parse local time for display purposes. Strip tzinfo for now; will add
        # timezone based on Strava's timezone field.
        local_start_time = datetime.fromisoformat(activity["start_date_local"]).replace(
            tzinfo=None
        )

        # Extract IANA timezone name from Strava's timezone field
        # e.g. "(GMT-08:00) America/Los_Angeles"
        timezone_str = activity.get("timezone", "")
        if timezone_str and ") " in timezone_str:
            # e.g. "America/Los_Angeles"
            tz_name = timezone_str.split(") ", 1)[-1]
            try:
                # Localize the datetime to get proper timezone abbreviation
                # e.g. "EST", "PDT", etc.
                tz = pytz.timezone(tz_name)
                local_start_time = tz.localize(local_start_time)
                local_time_str = local_start_time.strftime("%m/%d/%Y at %I:%M %p %Z")
            except pytz.exceptions.UnknownTimeZoneError:
                local_time_str = local_start_time.strftime("%m/%d/%Y at %I:%M %p")
        else:
            local_time_str = local_start_time.strftime("%m/%d/%Y at %I:%M %p")

        # Only create event if it doesn't already exist. I'm assuming that no
        # Strava events will ever overlap, so we can simply use
        # get_events_in_time_range(). This assumption might break in the future,
        # but for now seems to work fine (i.e. number of strava activites
        # matches number of create GCal events on a clean run).
        matching_events = google_calendar_api.get_events_in_time_range(
            service,
            GOOGLE_CALENDAR_STRAVA_CALENDAR_ID,
            start_time,
            end_time,
            UTC_STR,
        )
        # Build event object.
        new_event = _build_event(activity, start_time, end_time)

        # No events found, create new event.
        if len(matching_events) == 0:
            print()
            print(
                f"Creating Google Calendar event for activity '{activity['name']}' "
                f"on {local_time_str}."
            )
            if not dry_run:
                google_calendar_api.create_event(
                    service, GOOGLE_CALENDAR_STRAVA_CALENDAR_ID, new_event
                )
            created_events += 1
        # One event found, update if necessary.
        elif len(matching_events) == 1:
            existing_event = matching_events[0]
            diff = _compare_events(new_event, existing_event)
            if diff:
                diff_str = "".join(
                    [f"\n'{new_event[d]}' != '{existing_event[d]}'" for d in diff]
                )
                print()
                print(
                    f"Will update Google Calendar event for activity '{activity['name']}' "
                    f"on {local_time_str} "
                    f"because of following field diffs (format: 'new' != 'existing'): {diff_str}."
                )
                if not dry_run:
                    google_calendar_api.update_event(
                        service,
                        GOOGLE_CALENDAR_STRAVA_CALENDAR_ID,
                        existing_event["id"],
                        new_event,
                    )
                updated_events += 1
            else:
                non_modified_events += 1
        # Multiple events found, print error & skip.
        else:
            print()
            print(
                "ERROR: Multiple Google Calendar events found for single Strava "
                f"activity titled '{activity['name']}' "
                f"on {local_time_str}."
            )

    print()
    print(
        f"{mode}Created {created_events} new events, "
        f"updated {updated_events} existing events, "
        f"& skipped {non_modified_events} existing events. "
        f"Processed {len(all_activities)} activities."
    )

    return {
        "created": created_events,
        "updated": updated_events,
        "skipped": non_modified_events,
        "total": len(all_activities),
    }


if __name__ == "__main__":
    arg_parser = cli_args.build_sync_arg_parser(
        "Sync Strava activities to Google Calendar"
    )
    args = arg_parser.parse_args()

    # Toggle this to preview changes without modifying Google Calendar or
    # sending notifications
    DRY_RUN = False

    tz = time_utils.parse_timezone_arg(args.timezone)
    start_date = time_utils.parse_date_arg(args.start_date, tz)
    end_date = time_utils.parse_date_arg(args.end_date, tz)

    try:
        stats = strava_to_gcal(
            start_date,
            end_date,
            dry_run=DRY_RUN,
            force_refresh=args.force_refresh,
        )
        # Send success notification only if changes were made
        if DRY_RUN:
            print()
            print("Skipping ntfy.sh notification (dry run mode).")
            exit(0)
        if not (stats["created"] > 0 or stats["updated"] > 0):
            print()
            print("Skipping ntfy.sh success notification, no changes were made.")
            exit(0)
        if not args.notify_all:
            print()
            print(
                "Skipping ntfy.sh success notification, only sending failure notifications."
            )
            exit(0)

        title = "Strava to GCal - Success"
        message = (
            f"Successfully synced Strava activities to Google Calendar.\n\n"
            f"Dates: [{start_date.strftime('%m/%d/%Y')}, "
            f"{end_date.strftime('%m/%d/%Y')}]\n"
            f"Events created: {stats['created']}\n"
            f"Events updated: {stats['updated']}\n"
            f"Events skipped: {stats['skipped']}\n"
            f"Activities processed: {stats['total']}"
        )
        print()
        ntfy_api.send_notification(
            NTFY_TOPIC_URL,
            message,
            title=title,
            priority="default",
            tags=["white_check_mark"],
        )
    except Exception as e:
        # Send failure notification
        if not DRY_RUN:
            title = "Strava to GCal - Failed"
            error_trace = traceback.format_exc()
            message = f"Script failed with error:\n\n{str(e)}\n\n{error_trace}"
            print()
            ntfy_api.send_notification(
                NTFY_TOPIC_URL,
                message,
                title=title,
                priority="high",
                tags=["x", "warning"],
            )
        else:
            print()
            print("Skipping ntfy.sh failure notification (dry run mode).")
        # Re-raise the exception so the script still exits with an error code
        raise
