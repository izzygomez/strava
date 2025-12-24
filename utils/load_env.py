import os

from dotenv import load_dotenv

# Usage: this file should be imported at the beginning of any script that uses
# environment variables via a `from util.load_env import {vars...}` statement.

# Load environment variables from a .env file. `override` flag allows us to update .env vars.
load_dotenv(override=True)


def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value.strip()


### Get credentials from environment variables
# Strava
STRAVA_CLIENT_ID = get_env_var("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = get_env_var("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = get_env_var("STRAVA_REFRESH_TOKEN")
# Google Sheets
GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH = get_env_var(
    "GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH"
)
GOOGLE_SHEETS_SHEET_NAME = get_env_var("GOOGLE_SHEETS_SHEET_NAME")
# Google Calendar
GOOGLE_CALENDAR_JSON_CREDENTIALS_FULL_PATH = get_env_var(
    "GOOGLE_CALENDAR_JSON_CREDENTIALS_FULL_PATH"
)
GOOGLE_CALENDAR_STRAVA_CALENDAR_ID = get_env_var("GOOGLE_CALENDAR_STRAVA_CALENDAR_ID")
# ntfy.sh
NTFY_TOPIC_URL = get_env_var("NTFY_TOPIC_URL")
