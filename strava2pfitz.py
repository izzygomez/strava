import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dateutil import parser

# Load environment variables from a .env file. `override` flag allows us to update .env vars.
load_dotenv(override=True)

# Get credentials from environment variables
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH = os.getenv("GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH")
GOOGLE_SHEETS_SHEET_NAME = os.getenv("GOOGLE_SHEETS_SHEET_NAME")


def validate_env_vars():
    """Ensure all required environment variables are set."""
    required_vars = [
        "STRAVA_CLIENT_ID",
        "STRAVA_CLIENT_SECRET",
        "STRAVA_REFRESH_TOKEN",
        "GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH",
        "GOOGLE_SHEETS_SHEET_NAME",
    ]

    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(
                f"Environment variable {var} is not set or is empty."
            )


# Validate environment variables
validate_env_vars()

# DEBUG
# print("Strava Client ID:", STRAVA_CLIENT_ID)
# print("Strava Client Secret:", STRAVA_CLIENT_SECRET)
# print("Strava Refresh Token:", STRAVA_REFRESH_TOKEN)
# print("Google Sheets JSON Keyfile Full Path:", GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH)
# print("Google Sheets Sheet Name:", GOOGLE_SHEETS_SHEET_NAME)


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
    """Get all activities between the start and end date using the Strava API."""
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


def connect_to_google_sheets(json_keyfile_name, sheet_name):
    """Connect to a Google Sheet using the given JSON keyfile and sheet name."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_name, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet


def find_cell_index(sheet, header_name):
    """Find the index of the cell with the given header name."""
    for row_num in range(1, sheet.row_count + 1):
        row_values = sheet.row_values(row_num)
        for idx, value in enumerate(row_values):
            if value == header_name:
                return (
                    idx + 1,
                    row_num,
                )  # Return both column index and the row number where header is found
    raise ValueError(f"Header '{header_name}' not found.")


def get_emoji_for_activity_type(activity_type):
    """Return the appropriate emoji for the given activity type."""
    activity_emojis = {
        "Run": "🏃🏼‍♂️",
        "Ride": "🚴🏼‍♂️",
        "Swim": "🏊🏼‍♂️",
        "Walk": "🚶🏼‍♂️",
        "Hike": "🥾",
        "Yoga": "🧘‍♂️",
        "WeightTraining": "🏋🏼‍♂️",
        "Rowing": "🚣🏼‍♂️",
        "Workout": "💪🏼",
        "Crossfit": "🏋🏼‍♂️",
        "Kayaking": "🛶",
        "Canoeing": "🚣🏼‍♂️",
        "RockClimbing": "🧗🏼‍♂️",
        "Snowboarding": "🏂",
        "Skiing": "🎿",
        "IceSkate": "⛸️",
        "RollerSkate": "🛼",
        "EBikeRide": "🚴🏼‍♂️⚡",
    }
    return activity_emojis.get(
        activity_type, "???"
    )  # Default to question marks if type not found


def update_strava_links(sheet, strava_column, strava_row, date_column, activities):
    """Update cells under 'Strava Links' with multiple Strava activity links, using a single batch_update call."""
    date_cells = sheet.col_values(date_column)
    spreadsheet = sheet.spreadsheet
    requests = []

    # Mostly written with aid of ChatGPT & by adopting solution given here [1] because it was
    # suprisingly tricky to add multiple hyperlinks to a single cell. I mention the ChatGPT aid
    # here because I just wanted an MVP when first writing this, but looking at the code it seems
    # like it's a bit inefficient (e.g. iterating through all activities for each date cell) — can
    # choose to refactor this later if needed.
    # [1] https://stackoverflow.com/a/77312815
    for i in range(strava_row, len(date_cells)):
        date_value = date_cells[i]
        if not date_value:
            continue
        try:
            parsed_date = parser.parse(date_value).date()
        except ValueError:
            print(f"Skipping unrecognized date format: {date_value}")
            continue

        obj = []
        for activity in activities:
            activity_date = datetime.strptime(
                activity["start_date_local"][:10], "%Y-%m-%d"
            ).date()
            if activity_date == parsed_date:
                emoji = get_emoji_for_activity_type(activity["type"])
                text = f"{emoji} • {activity['name']}"
                url = f"https://www.strava.com/activities/{activity['id']}"
                obj.append({"t": text, "u": url})
        if obj:
            text = "\n".join([e["t"] for e in obj])
            requests.append(
                {
                    "updateCells": {
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {"stringValue": text},
                                        "textFormatRuns": [
                                            {"format": {"link": {"uri": e["u"]}}}
                                            for e in obj
                                        ],
                                    }
                                ]
                            }
                        ],
                        "range": {
                            "sheetId": sheet.id,
                            "startRowIndex": i,
                            "endRowIndex": i + 1,
                            "startColumnIndex": strava_column - 1,
                            "endColumnIndex": strava_column,
                        },
                        "fields": "userEnteredValue,textFormatRuns",
                    }
                }
            )

    if requests:
        spreadsheet.batch_update({"requests": requests})
        print(f"Updated {len(requests)} cells in the 'Strava Links' column.")


if __name__ == "__main__":
    ### Strava stuff
    # Strava API credentials
    # 1) Create a Strava App at https://www.strava.com/settings/api to get client_id & client_secret
    # 2) Get refresh_token by following the instructions at https://developers.strava.com/docs/getting-started/#oauth
    #    Note that this refresh token needs to have the 'activity:read_all' scope.
    access_token = get_strava_access_token(
        STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
    )

    # Define your date range. End date is non-inclusive.
    start_date = datetime(2024, 6, 17)
    end_date = datetime(2024, 10, 14)
    print("Fetching Strava activities from", start_date, "to", end_date)

    all_activities = get_strava_activities(access_token, start_date, end_date)
    # After fetching all activities, sort them by the start date. This will ensure they're in
    # the correct order when updating the Google Sheet.
    all_activities = sorted(
        all_activities, key=lambda x: datetime.fromisoformat(x["start_date_local"][:-1])
    )
    # print("length of all_activities: ", len(all_activities))  # DEBUG

    ### Google Sheets stuff
    # Connect to the Google Sheet
    # Credentials file that was downloaded from Google Developer Console after creating
    # a new project, enabling the Google Sheets API, & creating a service account.
    sheet = connect_to_google_sheets(
        GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH,
        GOOGLE_SHEETS_SHEET_NAME,
    )

    # Find the 'Strava Links' & 'Date' header cell locations
    strava_column, strava_row = find_cell_index(sheet, "Strava Links")
    date_column, date_row = find_cell_index(sheet, "Date")
    strava_a1 = gspread.utils.rowcol_to_a1(strava_row, strava_column)
    date_a1 = gspread.utils.rowcol_to_a1(date_row, date_column)
    # print(f"'Strava Links' header is at {strava_a1}")  # DEBUG
    # print(f"'Date' header is at {date_a1}")  # DEBUG

    # Ensure the date column and strava column headers are on the same row
    if date_row != strava_row:
        raise ValueError("'Date' and 'Strava Links' headers are not on the same row")

    # Update the 'Strava Links' column with Strava activity links
    update_strava_links(sheet, strava_column, strava_row, date_column, all_activities)
