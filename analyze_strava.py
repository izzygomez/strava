import os
from collections import defaultdict
from datetime import datetime

import pytz
from dotenv import load_dotenv

import strava

# Load environment variables from a .env file. `override` flag allows us to update .env vars.
load_dotenv(override=True)

# Get credentials from environment variables
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

### Strava stuff
# Strava API credentials
# 1) Create a Strava App at https://www.strava.com/settings/api to get client_id & client_secret
# 2) Get refresh_token by following the instructions at https://developers.strava.com/docs/getting-started/#oauth
#    Note that this refresh token needs to have the 'activity:read_all' scope.
ACCESS_TOKEN = strava.get_strava_access_token(
    STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
)


def erie_marathon_check():
    """just checking if Erie Marathon description still has URLs bc of associated Strava
    bug/regressions — seems like it got deleted grrrr"""

    # Define your date range. End date is non-inclusive.
    start_date = datetime(2024, 9, 8)
    end_date = datetime(2024, 9, 9)
    # print("Fetching Strava activities from", start_date, "to", end_date)

    all_activities = strava.get_strava_activities(ACCESS_TOKEN, start_date, end_date)
    # After fetching all activities, sort them by the start date. This will ensure they're in
    # the correct order when updating the Google Sheet.
    all_activities = sorted(
        all_activities, key=lambda x: datetime.fromisoformat(x["start_date_local"][:-1])
    )
    # print("length of all_activities: ", len(all_activities))  # DEBUG
    # for activity in all_activities:
    #     print(activity["name"], activity["start_date_local"], activity["distance"])
    # print(activity)  # DEBUG
    erie_marathon_summary = all_activities[1]

    erie_marathon_detailed = strava.get_strava_activity(
        ACCESS_TOKEN, erie_marathon_summary["id"]
    )
    for key, value in erie_marathon_detailed.items():
        print(key, ":", value, "\n")
    # print("Erie Marathon description:", erie_marathon_detailed["description"])


def longest_workout_breaks(additional_breaks=0):
    """Find the longest breaks between workouts since a given date.

    Prints the longest break and, if specified, the next 'additional_breaks' longest breaks.
    """

    # Define your date range. End date is non-inclusive.
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 10, 10)

    # Fetch Strava activities from the specified date range
    all_activities = strava.get_strava_activities(ACCESS_TOKEN, start_date, end_date)

    if len(all_activities) < 2:
        print("Not enough activities to calculate a break.")
        return

    # Sort activities by start date (already in local timezone per API docs)
    all_activities = sorted(
        all_activities, key=lambda x: datetime.fromisoformat(x["start_date_local"][:-1])
    )

    # DEBUG
    # print(
    #     "all_activities dates:",
    #     [activity["start_date_local"] for activity in all_activities],
    # )

    print(
        "Processing %d activities from Strava between %s & %s"
        % (len(all_activities), start_date.date(), end_date.date())
    )

    # Dictionary to store all breaks between workouts & the pair of dates
    # format: { break length -> [[start_date, end_date], ...] }
    breaks = defaultdict(list)

    for i, activity in enumerate(all_activities[:-1]):
        next_activity = all_activities[i + 1]

        # Convert both activity timestamps to correct local timezone based on the "timezone" field
        # The timezone field has the format '(GMT-05:00) America/New_York', so we split on the space and take the second part
        activity_timezone = pytz.timezone(activity["timezone"].split(" ")[1])
        next_activity_timezone = pytz.timezone(next_activity["timezone"].split(" ")[1])

        # Convert activity and next_activity to their respective timezones
        activity_date = (
            datetime.fromisoformat(activity["start_date_local"][:-1])
            .astimezone(activity_timezone)
            .date()
        )
        next_activity_date = (
            datetime.fromisoformat(next_activity["start_date_local"][:-1])
            .astimezone(next_activity_timezone)
            .date()
        )

        # Get the difference in days based on the calendar date, not the timestamp
        break_time = (
            next_activity_date - activity_date
        ).days - 1  # Subtract 1 to count full days between workouts

        # Let's ignore breaks of 1 day or less
        if break_time <= 1:
            continue

        breaks[break_time].append(
            [
                activity_date,
                next_activity_date,
            ]
        )

    if not breaks:
        print("No breaks found between activities.")
        return

    # Sort the breaks by the break length (in descending order)
    sorted_break_lengths = sorted(breaks.keys(), reverse=True)

    # Print the longest break
    longest_break = sorted_break_lengths[0]
    print("\nThe longest break (in days) between workouts is", longest_break, "days.")
    if len(breaks[longest_break]) > 1:
        print(
            "There are multiple breaks (%d) of this length. They are between:"
            % len(breaks[longest_break])
        )
        for longest_break_dates in breaks[longest_break]:
            print("\t- %s and %s." % tuple(longest_break_dates))
    else:
        longest_break_dates = breaks[longest_break][0]
        print(
            "This break was between %s and %s." % tuple(longest_break_dates),
        )

    # Print additional longest breaks if requested
    for i in range(1, min(additional_breaks + 1, len(sorted_break_lengths))):
        next_longest_break = sorted_break_lengths[i]
        print("\nThe next longest break (in days) is", next_longest_break, "days.")
        if len(breaks[next_longest_break]) > 1:
            print(
                "There are multiple breaks (%d) of this length. They are between:"
                % len(breaks[next_longest_break])
            )
            for break_dates in breaks[next_longest_break]:
                print("\t- %s and %s." % tuple(break_dates))
        else:
            break_dates = breaks[next_longest_break][0]
            print("This break was between %s and %s." % tuple(break_dates))


if __name__ == "__main__":
    # erie_marathon_check()
    longest_workout_breaks(additional_breaks=3)
