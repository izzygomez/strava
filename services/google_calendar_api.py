import os
from datetime import datetime
from pathlib import Path

import google
import pytz
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.load_env import GOOGLE_CALENDAR_JSON_CREDENTIALS_FULL_PATH

# If modifying these scopes, delete the token file.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN_FILE_NAME = str(_PROJECT_ROOT / "credentials" / "strava-to-gcal-token.json")


def _run_oauth_flow() -> (
    google.auth.external_account_authorized_user.Credentials
    | google.oauth2.credentials.Credentials
):
    """
    Run the OAuth flow to get user credentials.
    """
    flow = InstalledAppFlow.from_client_secrets_file(
        GOOGLE_CALENDAR_JSON_CREDENTIALS_FULL_PATH, SCOPES
    )
    return flow.run_local_server(port=0)


def create_google_calendar_service() -> object:
    """Create a Google Calendar service object."""
    creds = None
    # The token file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE_NAME):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_NAME, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                # Refresh token is invalid, re-run the OAuth flow.
                creds = _run_oauth_flow()
        else:
            creds = _run_oauth_flow()
        # Save the credentials for the next run
        os.makedirs(
            os.path.dirname(TOKEN_FILE_NAME), exist_ok=True
        )  # this ensures the directory exists
        with open(TOKEN_FILE_NAME, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def create_event(service, calendar_id, event) -> None:
    """Create an event on the specified calendar."""
    try:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Event created: {event.get('htmlLink')}.")
    except HttpError as error:
        print(f"An error occurred: {error}")


def get_events_in_time_range(
    service, calendar_id, start_time, end_time, time_zone
) -> list:
    """
    Return all events in the specified time range.
    Assumes the time range is small enough such that no pagination is needed.
    """
    try:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                timeZone=time_zone,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def get_all_events(service, calendar_id) -> list:
    """Get all events on the specified calendar."""
    try:
        all_events = []
        page_token = None
        pages_fetched = 0
        while True:
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    pageToken=page_token,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            all_events += events_result.get("items", [])
            page_token = events_result.get("nextPageToken")
            pages_fetched += 1
            if not page_token:
                break

        print(f"Fetched {len(all_events)} events from {pages_fetched} pages.")
        return all_events
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def delete_all_events(service, calendar_id) -> None:
    """Delete all events on the specified calendar."""
    try:
        events_result = (
            service.events()
            .list(calendarId=calendar_id, singleEvents=True, orderBy="startTime")
            .execute()
        )
        events = events_result.get("items", [])
        for event in events:
            service.events().delete(
                calendarId=calendar_id, eventId=event["id"]
            ).execute()
            print(f"Deleted event: {event['summary']}.")
    except HttpError as error:
        print(f"An error occurred: {error}")


def update_event(service, calendar_id, event_id, event) -> None:
    """Update an event on the specified calendar."""
    try:
        updated_event = (
            service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event)
            .execute()
        )
        print(f"Event updated: {updated_event.get('htmlLink')}.")
    except HttpError as error:
        print(f"An error occurred: {error}")


def list_upcoming_events(service, max_results=10) -> None:
    """Shows basic usage of the Google Calendar API.
    Prints the start & name of the next max_results events on primary calendar.
    """
    try:
        local_tz = pytz.timezone("America/New_York")
        now = datetime.now(local_tz).astimezone(pytz.utc).isoformat()
        # print(f"{now=}")  # DEBUG
        print(f"Getting the upcoming {max_results} events on primary calendar.")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
    except HttpError as error:
        print(f"An error occurred: {error}")


def list_all_calendars(service) -> None:
    """List all calendars the user has access to."""
    print("Getting all calendars.")
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list["items"]:
            print(f"{calendar_list_entry['summary']} (id: {calendar_list_entry['id']})")
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break
