import os
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
    Helper function to log activities either to console (file_name='') or to a file. Formatting across both options is consistent. Files will be saved in the 'exports' directory at the root of the project.
    """

    def _log_activities(activities, file=None):
        main_header = f"Total activities: {len(activities)}\n"
        if file:
            file.write(main_header)
        else:
            print(main_header)

        for sport_type in strava_api.SPORT_TYPE_TO_EMOJI.keys():
            filtered_activities = [
                activity
                for activity in activities
                if activity["sport_type"] == sport_type
            ]
            if not filtered_activities:
                continue

            sport_type_header = f"{sport_type} ({len(filtered_activities)} activities):"
            if file:
                file.write("\n" + sport_type_header)
            else:
                print(sport_type_header)

            for activity in filtered_activities:
                activity_str = (
                    f"{activity['name']} on "
                    f"{datetime.fromisoformat(activity['start_date_local']).strftime('%m/%d/%Y')}: "
                    f"{strava_api.get_activity_url(activity['id'])}"
                )
                if file:
                    file.write("\n" + activity_str)
                else:
                    print(activity_str)

            if file:
                file.write("\n")
            else:
                print()

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
    start_date = datetime(2025, 1, 1)
    end_date = time_utils.n_days_from_today(1)

    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date
    )

    print()
    log_activities(activities)


def write_all_activities_to_file():
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.n_days_from_today(1)

    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date
    )

    file_name = "strava-all-activities-export.txt"
    log_activities(activities, file_name=file_name)


def write_all_workout_activities_to_file():
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.n_days_from_today(1)

    sport_type_filters = ["Workout"]
    activities = strava_api.get_sorted_strava_activities(
        ACCESS_TOKEN, start_date, end_date, sport_type_filters=sport_type_filters
    )

    file_name = "strava-workout-activities-export.txt"
    log_activities(activities, file_name=file_name)


def fix_soccer_activities():
    """
    Iterate through all 'Workout' activities that have soccer emoji & update
    them to have the 'Soccer' SportType. This is a one-time fix, & should no
    longer be necessary to run after the initial run.
    """
    start_date = time_utils.izzys_strava_start_date()
    end_date = time_utils.n_days_from_today(1)

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


if __name__ == "__main__":
    ### Misc functions that I'm currently toying with

    log_2025_activities_to_console()

    # write_all_activities_to_file()

    # write_all_workout_activities_to_file()

    # fix_soccer_activities()
