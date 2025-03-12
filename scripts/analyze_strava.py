from collections import defaultdict
from datetime import datetime, timedelta

import pytz

from services import strava_api
from utils import time_utils
from utils.load_env import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN

ACCESS_TOKEN = strava_api.get_strava_access_token(
    STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
)


def erie_marathon_check():
    """just checking if Erie Marathon description still has URLs bc of associated Strava
    bug/regressions — seems like it got deleted grrrr"""

    # Define your date range. End date is non-inclusive.
    start_date = datetime(2024, 9, 8)
    end_date = datetime(2024, 9, 9)

    all_activities = strava_api.get_strava_activities(
        ACCESS_TOKEN, start_date, end_date, log=True
    )

    # print("length of all_activities: ", len(all_activities))  # DEBUG
    # for activity in all_activities:
    #     print(activity["name"], activity["start_date"], activity["distance"])
    # print(activity)  # DEBUG
    erie_marathon_summary = all_activities[1]

    erie_marathon_detailed = strava_api.get_strava_activity(
        ACCESS_TOKEN, erie_marathon_summary["id"]
    )
    for key, value in erie_marathon_detailed.items():
        print(key, ":", value, "\n")
    # print("Erie Marathon description:", erie_marathon_detailed["description"])


# TODO consider adding an optional filter for different sport types, e.g. only runs
def longest_workout_breaks(
    start_date: datetime, end_date: datetime, additional_breaks=0, sport_type=None
):
    """Find the longest breaks in [start_date, end_date).

    Prints the longest break &, if specified, the next 'additional_breaks' longest breaks.
    """
    all_activities = strava_api.get_strava_activities(
        ACCESS_TOKEN, start_date, end_date
    )

    if len(all_activities) < 2:
        print("Not enough activities to calculate a break.")
        return

    # DEBUG
    # print(
    #     "all_activities dates:",
    #     [activity["start_date_local"] for activity in all_activities],
    # )

    print(
        "Processing %d activities from Strava from %s to %s (inclusive)."
        % (len(all_activities), start_date.date(), end_date.date() - timedelta(days=1))
    )

    # Dictionary to store all breaks between workouts & the pair of dates
    # format: { break length -> [[start_date, end_date], ...] }
    breaks = defaultdict(list)

    for i, activity in enumerate(all_activities[:-1]):
        next_activity = all_activities[i + 1]

        # Convert both activity timestamps to correct local timezone based on the "timezone" field
        # The timezone field has the format '(GMT-05:00) America/New_York', so we split on the space & take the second part
        activity_timezone = pytz.timezone(activity["timezone"].split(" ")[1])
        next_activity_timezone = pytz.timezone(next_activity["timezone"].split(" ")[1])

        # Convert activity & next_activity to their respective timezones
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
                activity_date + timedelta(days=1),
                next_activity_date - timedelta(days=1),
            ]
        )

    if not breaks:
        print("No breaks found between activities.")
        return

    # Sort the breaks by the break length (in descending order)
    sorted_break_lengths = sorted(breaks.keys(), reverse=True)

    # Print the longest break
    longest_break = sorted_break_lengths[0]
    print("\nThe longest break between workouts was", longest_break, "days.")
    if len(breaks[longest_break]) > 1:
        print(
            "There are multiple (%d) breaks of this length. They were from:"
            % len(breaks[longest_break])
        )
        for longest_break_dates in breaks[longest_break]:
            print("\t- %s to %s." % tuple(longest_break_dates))
    else:
        longest_break_dates = breaks[longest_break][0]
        print(
            "This break was from %s to %s." % tuple(longest_break_dates),
        )

    # Print additional longest breaks if requested
    for i in range(1, min(additional_breaks + 1, len(sorted_break_lengths))):
        next_longest_break = sorted_break_lengths[i]
        print("\nThe next longest break was", next_longest_break, "days.")
        if len(breaks[next_longest_break]) > 1:
            print(
                "There are multiple (%d) breaks of this length. They were from:"
                % len(breaks[next_longest_break])
            )
            for break_dates in breaks[next_longest_break]:
                print("\t- %s to %s." % tuple(break_dates))
        else:
            break_dates = breaks[next_longest_break][0]
            print("This break was from %s to %s." % tuple(break_dates))


if __name__ == "__main__":
    # erie_marathon_check()

    start_date = datetime(2024, 1, 1)
    tomorrow = time_utils.n_days_from_today(1)
    longest_workout_breaks(start_date, tomorrow, additional_breaks=3)
