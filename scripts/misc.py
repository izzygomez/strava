import os
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


if __name__ == "__main__":
    ### Misc functions that I'm currently toying with
    # log_2025_activities_to_console()
    # write_all_activities_to_file()
    # write_all_workout_activities_to_file()

    ### One-time fixes
    # fix_soccer_activities()
    # fix_basketball_activities()
    # fix_volleyball_activities()
    pass
