import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parent.parent / ".strava_cache"
CACHE_FILE = CACHE_DIR / "strava_activities_cache.json"
CACHE_TTL_HOURS = 1


def _load_cache() -> dict | None:
    """Load cache from file. Returns None if cache doesn't exist or is invalid."""
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
        print("Skipping cache load.")
        return None


def _save_cache(start_date: datetime, end_date: datetime, activities: list) -> None:
    """Save activities to cache file with metadata."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_data = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "activities": activities,
    }
    with open(CACHE_FILE, "w") as f:
        json.dump(cache_data, f)


def _is_cache_valid(cache: dict, start_date: datetime, end_date: datetime) -> bool:
    """
    Check if cache is valid for the requested date range.

    Returns True if:
    - Cache is less than CACHE_TTL_HOURS old
    - Requested [start_date, end_date) is fully contained within cached range
    """
    try:
        cached_at = datetime.fromisoformat(cache["cached_at"])
        cached_start = datetime.fromisoformat(cache["start_date"])
        cached_end = datetime.fromisoformat(cache["end_date"])
    except (KeyError, ValueError):
        return False

    # cached_at should always be set to UTC for comparison
    if cached_at.tzinfo is None:
        cached_at = cached_at.replace(tzinfo=timezone.utc)

    # check if cache is expired
    cache_age = datetime.now(timezone.utc) - cached_at
    if cache_age > timedelta(hours=CACHE_TTL_HOURS):
        return False

    # use timestamps for comparison
    return (
        cached_start.timestamp() <= start_date.timestamp()
        and cached_end.timestamp() >= end_date.timestamp()
    )


def _filter_activities_by_date(
    activities: list, start_date: datetime, end_date: datetime
) -> list:
    """Filter activities to only include those within [start_date, end_date)."""
    filtered = []
    for activity in activities:
        activity_start = datetime.fromisoformat(activity["start_date"])
        # Convert to timestamp for comparison to handle timezone differences
        if start_date.timestamp() <= activity_start.timestamp() < end_date.timestamp():
            filtered.append(activity)
    return filtered


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


def get_sorted_strava_activities(
    access_token,
    start_date,
    end_date,
    sport_type_filters=set(),
    page_size=200,
    force_refresh=False,
) -> list:
    """
    Get all Strava activities in [start_date, end_date) using the Strava API.
    Will return sorted by start date.

    Results are cached for 1 hour. Cache is used if:
    - force_refresh is False
    - Cache exists and is less than 1 hour old
    - Requested date range is fully contained within cached date range

    Note that this endpoint [1] returns an array of SummaryActivity [2] objects,
    which may not contain all the data associated with an activity. If you need
    more details, you can use the /activities/{id} endpoint [3] in
    get_strava_activity() to get the full activity details.

    [1] https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
    [2] https://developers.strava.com/docs/reference/#api-models-SummaryActivity
    [3] https://developers.strava.com/docs/reference/#api-Activities-getActivityById
    """
    # check cache first, unless force_refresh is True
    if not force_refresh:
        cache = _load_cache()
        if cache and _is_cache_valid(cache, start_date, end_date):
            print(
                f"Using cached Strava activities for range [{start_date.strftime('%m/%d/%Y')}, "
                f"{end_date.strftime('%m/%d/%Y')})..."
            )
            all_activities = cache["activities"]
            # Filter to requested date range
            all_activities = _filter_activities_by_date(
                all_activities, start_date, end_date
            )
            print()
            print(f"Found {len(all_activities)} activities in cache.")
            return _apply_sport_type_filter(all_activities, sport_type_filters)

    # cache miss or force_refresh -> fetch from API
    all_activities = _fetch_activities_from_api(
        access_token, start_date, end_date, page_size
    )

    # save to cache, before sport_type filtering to maximize cache reuse
    _save_cache(start_date, end_date, all_activities)

    return _apply_sport_type_filter(all_activities, sport_type_filters)


def _fetch_activities_from_api(access_token, start_date, end_date, page_size) -> list:
    """Fetch activities from Strava API and return sorted by start date."""
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

    # Sort by start date. All start date values are in UTC per the API docs.
    all_activities = sorted(
        all_activities, key=lambda x: datetime.fromisoformat(x["start_date"])
    )
    print()
    print(f"Fetched {len(all_activities)} Strava activities")

    return all_activities


def _apply_sport_type_filter(activities: list, sport_type_filters) -> list:
    """Filter activities by sport_type if filters are specified."""
    if not sport_type_filters:
        return activities

    filtered_activities = [
        activity
        for activity in activities
        if activity["sport_type"] in sport_type_filters
    ]
    print()
    print(
        f"Filtered down to {len(filtered_activities)} activities of sport type(s): {sport_type_filters}"
    )
    return filtered_activities


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
