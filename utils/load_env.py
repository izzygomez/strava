import os
from pathlib import Path

from dotenv import load_dotenv

# Usage: this file should be imported at the beginning of any script that uses
# environment variables via a `from util.load_env import {vars...}` statement.

# Load environment variables from the project root .env file, regardless of
# working directory from which the script is invoked.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)


def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise OSError(f"Missing required environment variable: {var_name}")
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
GOOGLE_SHEETS_SPREADSHEET_ID = get_env_var("GOOGLE_SHEETS_SPREADSHEET_ID")
# Google Calendar
GOOGLE_CALENDAR_JSON_CREDENTIALS_FULL_PATH = get_env_var(
    "GOOGLE_CALENDAR_JSON_CREDENTIALS_FULL_PATH"
)
GOOGLE_CALENDAR_STRAVA_CALENDAR_ID = get_env_var("GOOGLE_CALENDAR_STRAVA_CALENDAR_ID")
# ntfy.sh
NTFY_TOPIC_URL = get_env_var("NTFY_TOPIC_URL")
