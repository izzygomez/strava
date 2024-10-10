import requests


def get_strava_access_token(client_id, client_secret, refresh_token):
    """Get a new access token using the Strava API."""
    try:
        response = requests.post(
            url="https://www.strava.com/oauth/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
                "f": "json",
            },
        )
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Failed to get Strava access token: {e}")
        raise


def get_strava_activities(access_token, start_date, end_date, per_page=200):
    """Get all activities in [start_date, end_date) using the Strava API. Not sorted.

    Note that this endpoint [1] returns an array of SummaryActivity [2] objects, which may not
    contain all the data associated with an activity. If you need more details, you can use the
    /activities/{id} endpoint [3] to get the full activity details.
    [1] https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
    [2] https://developers.strava.com/docs/reference/#api-models-SummaryActivity
    [3] https://developers.strava.com/docs/reference/#api-Activities-getActivityById
    """
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}

    all_activities = []
    page = 1

    while True:
        params = {
            "after": start_date.timestamp(),
            "before": end_date.timestamp(),
            "per_page": per_page,
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

    # print("number of API calls made to get all_activities: ", page - 1)  # DEBUG
    return all_activities


def get_strava_activity(access_token, activity_id):
    """Get a single activity using the Strava API."""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch activity from Strava: {e}")
        raise
