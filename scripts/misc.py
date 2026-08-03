import os
import re
from collections import defaultdict
from datetime import datetime

from services import strava_api
from utils import time_utils
from utils.load_env import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN

# Find or create the 'exports' directory at the root of the project.
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)  # Ensure the directory exists

ACCESS_TOKEN = strava_api.get_strava_access_token(
    STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
)


def log_activities(activities, file_name=""):
    """
    Helper function to log activities either to console (file_name="") or to a
    file. Formatting across both options is consistent. Files will be saved in
    the exports/ directory at the root of the project.
    """

    def _log_activities(activities, file=None):
        """Render grouped activity output to either file or stdout."""

        def _write_line(line=""):
            """Write one line to the selected output target."""
            if file:
                file.write(f"{line}\n")
            else:
                print(line)

        def _format_activity(activity):
            """Format one activity as a display/export line."""
            return (
                f"{activity['name']} on "
                f"{datetime.fromisoformat(activity['start_date_local']).strftime('%m/%d/%Y')}: "
                f"{strava_api.get_activity_url(activity['id'])}"
            )

        timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        _write_line(f"Total activities: {len(activities)}")
        _write_line(f"Export created: {timestamp}")

        activities_by_sport_type = defaultdict(list)
        for activity in activities:
            activities_by_sport_type[activity["sport_type"]].append(activity)

        mapped_sport_types = sorted(strava_api.SPORT_TYPE_TO_EMOJI.keys())
        mapped_sport_type_set = set(mapped_sport_types)

        def _render_sport_type_section(sport_type):
            """Render one sport type section if it has activities."""
            filtered_activities = activities_by_sport_type.get(sport_type, [])
            if not filtered_activities:
                return

            _write_line()
            _write_line(f"{sport_type} ({len(filtered_activities)} activities):")
            for activity in filtered_activities:
                _write_line(_format_activity(activity))

        for sport_type in mapped_sport_types:
            _render_sport_type_section(sport_type)

        # Sport types that exist in data but are not yet mapped to emojis in
        # SPORT_TYPE_TO_EMOJI dict.
        unmapped_sport_types = sorted(
            sport_type
            for sport_type in activities_by_sport_type.keys()
            if sport_type not in mapped_sport_type_set
        )
        if not unmapped_sport_types:
            return

        _write_line()
        _write_line("Unmapped sport types:")
        for sport_type in unmapped_sport_types:
            _render_sport_type_section(sport_type)

    if file_name:
        file_path = os.path.join(EXPORTS_DIR, file_name)
        print(f"Logging activities to {file_path}...")
        with open(file_path, "w") as f:
            _log_activities(activities, file=f)
    else:
        print("Logging activities to console...")
        print()
        _log_activities(activities)


def log_2025_activities_to_console():
    """Export 2025-to-date activities to console for quick inspection."""
    start_date = datetime(2025, 1, 1, tzinfo=time_utils.EASTERN)
    end_date = time_utils.today()

    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date
    )

    print()
    log_activities(activities)


def write_all_activities_to_file():
    """Write all activities to a timestamped export file."""
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.today()

    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date
    )

    timestamp_prefix = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{timestamp_prefix}_strava-all-activities-export.txt"
    log_activities(activities, file_name=file_name)


def write_all_workout_activities_to_file():
    """Write only Workout sport_type activities to a timestamped file."""
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.today()

    sport_type_filters = ["Workout"]
    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date, sport_type_filters=sport_type_filters
    )

    timestamp_prefix = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{timestamp_prefix}_strava-workout-activities-export.txt"
    log_activities(activities, file_name=file_name)


### One-time fixes
def fix_soccer_activities():
    """
    Iterate through all 'Workout' activities that have soccer emoji & update
    them to have the 'Soccer' SportType. This is a one-time fix, & should no
    longer be necessary to run after the initial run.
    """
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.today()

    sport_type_filters = ["Workout"]
    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date, sport_type_filters=sport_type_filters
    )
    soccer_activities = [
        activity for activity in activities if "⚽" in activity["name"]
    ]
    print(f"Found {len(soccer_activities)} soccer activities.")

    for activity in soccer_activities:
        print()
        strava_api.update_strava_activity(
            ACCESS_TOKEN, activity_id=activity["id"], data={"sport_type": "Soccer"}
        )


def fix_basketball_activities():
    """
    Iterate through all 'Workout' activities that have basketball emoji & update
    them to have the 'Basketball' SportType. This is a one-time fix, & should no
    longer be necessary to run after the initial run.
    """
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.today()

    sport_type_filters = ["Workout"]
    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date, sport_type_filters=sport_type_filters
    )
    basketball_activities = [
        activity for activity in activities if "🏀" in activity["name"]
    ]
    print(f"Found {len(basketball_activities)} basketball activities.")

    for activity in basketball_activities:
        print()
        strava_api.update_strava_activity(
            ACCESS_TOKEN, activity_id=activity["id"], data={"sport_type": "Basketball"}
        )


def fix_volleyball_activities():
    """
    Iterate through all 'Workout' activities that have volleyball emoji & update
    them to have the 'Volleyball' SportType. This is a one-time fix, & should no
    longer be necessary to run after the initial run.
    """
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.today()

    sport_type_filters = ["Workout"]
    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date, sport_type_filters=sport_type_filters
    )
    volleyball_activities = [
        activity for activity in activities if "🏐" in activity["name"]
    ]
    print(f"Found {len(volleyball_activities)} volleyball activities.")

    for activity in volleyball_activities:
        print()
        strava_api.update_strava_activity(
            ACCESS_TOKEN, activity_id=activity["id"], data={"sport_type": "Volleyball"}
        )


def fix_description_url_dots(
    dry_run: bool = True,
    max_activities: int | None = None,
    race_only: bool = False,
):
    """
    Replace '(dot)' with '.' only inside URL-like text in activity descriptions.

    This is a one-time fix. The context here is that for some time — while
    Strava was getting their shit together with respect to URL support in
    activity titles & descriptions (see [1]) — I ended up using '(dot)' instead
    of '.' in URLs to get around the temporary URL ban, because I didn't want to
    lose my data. However, when URL support was restored, Strava didn't go back
    & fix the activities it had deleted before, so there was an explicit need
    for this manual fix. This is what this function is for.

    Defaults to dry run mode & prints proposed changes without updating Strava.
    Uses detailed activity fetches because activities returned by
    get_sorted_strava_activities() omits description text.

    If race_only=True, only inspect activities with workout types marked as
    race. If max_activities is set, only scan that many activities from the
    filtered list. These two flags are useful because otherwise I'd hit my rate
    limit pretty quickly (making an extra get_strava_activity() API call for
    each activity).

    [1] https://web.archive.org/web/20260211070415/https://support.strava.com/hc/en-us/articles/34413026584461-Links-on-Strava
    """
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.today()
    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date
    )
    if race_only:
        # workout_type is legacy but still used by Strava to mark race workouts:
        # run race = 1, ride race = 11. from:
        # https://communityhub.strava.com/developers-api-7/identifying-workouts-from-summaryactivity-object-2001
        race_workout_types = {1, 11}
        activities = [
            activity
            for activity in activities
            if activity.get("workout_type") in race_workout_types
        ]
        print(
            f"Filtered to {len(activities)} race activity summaries "
            "(workout_type in {1, 11})."
        )
    if max_activities is not None:
        activities = activities[:max_activities]
        print(
            f"Scanning first {len(activities)} activities "
            f"(max_activities={max_activities})."
        )
    else:
        print(f"Scanning all {len(activities)} activities.")

    # URL-like token containing one or more "(dot)" sequences.
    # Examples matched:
    # - "https://example(dot)com/path"
    # - "www.example(dot)com"
    # - "example(dot)com"
    broken_url_pattern = re.compile(
        r"((?:https?://|www\.)?\b[\w-]+(?:\(dot\)[\w-]+)+(?:/[^\s]*)?)",
        re.IGNORECASE,
    )

    candidates_found = 0
    inspected_count = 0
    updated_count = 0
    for activity in activities:
        inspected_count += 1
        detailed_activity = strava_api.get_strava_activity(ACCESS_TOKEN, activity["id"])
        description = detailed_activity.get("description")
        if not description or "(dot)" not in description:
            continue

        def _fix_match(match):
            return match.group(1).replace("(dot)", ".")

        updated_description, replacements = broken_url_pattern.subn(
            _fix_match, description
        )
        if replacements == 0 or updated_description == description:
            continue

        candidates_found += 1
        print()
        print(
            f"Activity {activity['id']} - '{activity['name']}' has {replacements} "
            "URL replacement(s)."
        )
        print(f"Strava URL: {strava_api.get_activity_url(activity['id'])}")
        # print(f"Before: {description}")  # DEBUG
        # print(f"After:  {updated_description}")  # DEBUG

        if dry_run:
            continue

        strava_api.update_strava_activity(
            ACCESS_TOKEN,
            activity_id=activity["id"],
            data={"description": updated_description},
        )
        updated_count += 1

    print()
    print(f"Inspected {inspected_count} detailed activities.")
    print(f"Found {candidates_found} activity description(s) with broken URL text.")
    if dry_run:
        print("Dry run mode enabled; no Strava activity descriptions were updated.")
    else:
        print(f"Updated {updated_count} activity description(s).")


if __name__ == "__main__":
    ### Misc functions that I'm currently toying with
    # log_2025_activities_to_console()
    # write_all_activities_to_file()
    # write_all_workout_activities_to_file()

    ### One-time fixes
    # fix_soccer_activities()
    # fix_basketball_activities()
    # fix_volleyball_activities()
    # fix_description_url_dots(dry_run=True, race_only=True)
    pass
