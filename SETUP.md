# Setup

This document describes the steps required to set up external integrations. Important & sensitive values are then stored in `.env`, which is in `.gitignore` to avoid leaking publicly.

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Pre-commit

This project uses [pre-commit](https://pre-commit.com/) to run code formatting & linting checks before each commit. To install the pre-commit hooks, run:

```bash
pre-commit install
```

To run checks manually on all files:

```bash
pre-commit run --all-files --verbose
```

## Strava Integration

Relevant links: [Strava Developers landing page](https://developers.strava.com/), [API reference](https://developers.strava.com/docs/reference/).

1. Create a new application on the [Strava API](https://www.strava.com/settings/api) settings page to get a `client_id` & a `client_secret`.
1. Follow instructions on the [Strava API authentication page](https://developers.strava.com/docs/authentication/) to get a `refresh_token`.

   1. On Web, open the following URL with the appropriate values set:

      `https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read_all,activity:read_all,activity:write`

   1. Click "Authorize". You'll be redirected to a `localhost/*` URL with a `code` query parameter. Copy this value.

   1. This `code` can be used with `client_id` & `client_secret` to acquire a refresh token. Use the following POST request:

      ```bash
      curl -X POST https://www.strava.com/api/v3/oauth/token  \
        -d client_id={CLIENT_ID} \
        -d client_secret={CLIENT_SECRET} \
        -d code={CODE} \
        -d grant_type=authorization_code
      ```

      This will return a JSON response with a `refresh_token` field.

1. Set `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, & `STRAVA_REFRESH_TOKEN` appropriately in the `.env` file.

## Google Integrations

I decided to create separate Google Cloud Platform projects for the Google Sheets & Google Calendar integrations. Mostly to keep privileges separate, but also just a style choice.

### Integrations for strava_to_pfitz_gsheet.py

1. Create a new Google Cloud Platform project to manage connections used by `strava_to_pfitz_gsheet.py`. I chose to name mine "Strava to Pfitz GSheet".

1. Enable the Google Sheets & the Google Drive APIs for this new project.

1. Under IAM & Admin > Service accounts, create a new service account for the project.

1. Create & download a new JSON key for this new service account. Save in this repo. Set the `GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH` environment variable to the path of the JSON file.

1. Locate Google Sheet that you want to modify with the `strava_to_pfitz_gsheet.py` script. Set the `GOOGLE_SHEETS_SHEET_NAME` environment variable to the name of the sheet.

1. Add service account email address to sheet with the `Editor` role.

### Integrations for strava_to_gcal.py

1. Create a new Google Cloud Platform project for to manage connections used by `strava_to_gcal.py`. I chose to name mine "Strava to GCal".

1. Enable the Google Calendar API for this new project.

1. Following the [Google Calendar API Python Quickstart](https://developers.google.com/calendar/api/quickstart/python) instructions:

   1. Under Google Auth platform > Clients, create a new OAuth 2.0 Client ID. Set the application type to "Desktop app".

   1. Download the credentials JSON & save in this repo. Set the `GOOGLE_CALENDAR_JSON_CREDENTIALS_FULL_PATH` environment variable to the path of the JSON file.

   1. Don't run script yet, finish rest of setup instructions. But note that on first run, you'll be redirected to authenticate with Google. A `strava-to-gcal-token.json` file will then automatically be created in the same directoy where the script is run, so ensure that you run from project root. As before, this token file should not be committed, & is ignored by `.gitignore`.

1. Set the `GOOGLE_CALENDAR_STRAVA_CALENDAR_ID` environment variable to the ID of the Google Calendar you want to add events to. If set to your gmail address, events will be added to your primary calendar. But it's preferable to create a dedicated calendar & using the `*@group.calendar.google.com` ID.
