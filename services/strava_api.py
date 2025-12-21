from datetime import datetime

import requests

# Gathered list from [1]. Note that this may not be up-to-date, & that this is
# distinct from ActivityType [2].
# [1] https://developers.strava.com/docs/reference/#api-models-SportType
# [2] https://developers.strava.com/docs/reference/#api-models-ActivityType
SPORT_TYPE_TO_EMOJI = {
    "AlpineSki": "⛷️",
    "BackcountrySki": "🎿",
    "Badminton": "🏸",
    "Canoeing": "🚣🏼‍♂️",
    "Crossfit": "🏋🏼‍♂️",
    "EBikeRide": "🚴🏼‍♂️⚡",
    "Elliptical": "🚴🏼‍♂️",
    "EMountainBikeRide": "🚴🏼‍♂️⚡",
    "Golf": "🏌️‍♂️",
    "GravelRide": "🚴🏼‍♂️",
    "Handcycle": "👋🏼🚴🏼‍♂️",
    "HighIntensityIntervalTraining": "🏋🏼‍♂️",
    "Hike": "🥾",
    "IceSkate": "⛸️",
    "InlineSkate": "🛼",
    "Kayaking": "🛶",
    "Kitesurf": "🪁🏄‍♂️",
    "MountainBikeRide": "🚵🏼‍♂️",
    "NordicSki": "🎿",
    "Pickleball": "🏓",
    "Pilates": "🧘‍♂️",
    "Racquetball": "🏸",
    "Ride": "🚴🏼‍♂️",
    "RockClimbing": "🧗🏼‍♂️",
    "RollerSki": "🎿",
    "Rowing": "🚣🏼‍♂️",
    "Run": "🏃🏼‍♂️",
    "Sail": "⛵",
    "Skateboard": "🛹",
    "Snowboard": "🏂",
    "Snowshoe": "❄️👟",
    "Soccer": "⚽",
    "Squash": "🏸",
    "StairStepper": "🪜",
    "StandUpPaddling": "🧍🏼‍♂️🚤",
    "Surfing": "🏄‍♂️",
    "Swim": "🏊🏼‍♂️",
    "TableTennis": "🏓",
    "Tennis": "🎾",
    "TrailRun": "🏃🏼‍♂️",
    "Velomobile": "🚗",
    "VirtualRide": "🚴🏼‍♂️",
    "VirtualRow": "🚣🏼‍♂️",
    "VirtualRun": "🏃🏼‍♂️",
    "Walk": "🚶🏼‍♂️",
    "WeightTraining": "🏋🏼‍♂️",
    "Wheelchair": "🧑‍🦽",
    "Windsurf": "💨️️️️️️️️️️️️️️️️️️🏄‍♂️",
    "Workout": "💪🏼",
    "Yoga": "🧘‍♂️",
}


def get_emoji_for_sport_type(sport_type) -> str:
    return SPORT_TYPE_TO_EMOJI.get(sport_type, "???")


def get_activity_url(activity_id):
    return f"https://www.strava.com/activities/{activity_id}"


def get_strava_access_token(client_id, client_secret, refresh_token):
    """Get a new access token using the Strava API."""
    response = requests.post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "f": "json",
        },
        timeout=30,
    )
    if not response.ok:
        # Strava often returns a helpful JSON error body; include it for debugging.
        details = response.text.strip()
        raise requests.exceptions.HTTPError(
            f"{response.status_code} {response.reason} from Strava oauth/token"
            + (f":\n{details}" if details else ""),
            response=response,
        )
    return response.json()["access_token"]


# TODO: add caching for ~1 hour, can be skipped by passing in a flag
def get_sorted_strava_activities(
    access_token, start_date, end_date, sport_type_filters=set(), page_size=200
) -> list:
    """
    Get all Strava activities in [start_date, end_date) using the Strava API.
    Will return sorted by start date.

    Note that this endpoint [1] returns an array of SummaryActivity [2] objects,
    which may not contain all the data associated with an activity. If you need
    more details, you can use the /activities/{id} endpoint [3] in
    get_strava_activity() to get the full activity details.

    [1] https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
    [2] https://developers.strava.com/docs/reference/#api-models-SummaryActivity
    [3] https://developers.strava.com/docs/reference/#api-Activities-getActivityById
    """
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = _create_headers(access_token)

    print(
        f"Fetching Strava activities in range [{start_date.strftime('%m/%d/%Y')}, "
        f"{end_date.strftime('%m/%d/%Y')})..."
    )

    all_activities = []
    page = 1

    while True:
        params = {
            "after": start_date.timestamp(),
            "before": end_date.timestamp(),
            "per_page": page_size,
            "page": page,
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            activities = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch activities from Strava: {e}")
            raise

        if not activities:
            break

        all_activities.extend(activities)
        page += 1
    # print()
    # print(f"number of API calls made to get all_activities: {page - 1}")  # DEBUG

    # After fetching all activities, sort them by the start date. All start
    # date values are in UTC per the API docs.
    all_activities = sorted(
        all_activities, key=lambda x: datetime.fromisoformat(x["start_date"])
    )
    print()
    print(f"Fetched {len(all_activities)} Strava activities.")

    # Filter activities by sport_type if specified
    if sport_type_filters:
        filtered_activities = [
            activity
            for activity in all_activities
            if activity["sport_type"] in sport_type_filters
        ]
        print()
        print(
            f"Filtered down to {len(filtered_activities)} activities of sport type(s): {sport_type_filters}"
        )
        return filtered_activities
    else:
        return all_activities


def get_strava_activity(access_token, activity_id):
    """Get a single activity using the Strava API."""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = _create_headers(access_token)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch activity from Strava: {e}")
        raise


def update_strava_activity(access_token, activity_id, data):
    """Update an activity using the Strava API."""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = _create_headers(access_token)

    try:
        print(f"Updating activity (id = {activity_id}) with data {data}...")
        # note: this is a PUT request
        response = requests.put(url, headers=headers, data=data)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to update activity from Strava: {e}")
        raise


def _create_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}
