# Setup

This document describes the steps required to set up external integrations. Sensitive environment variables are stored in `.env` & credential files are stored in the `credentials/` directory, both of which are ignored by `.gitignore` to avoid leaking publicly.

<details>
<summary><h2>Requirements</h2></summary>

Install the required dependencies:

```bash
pip install -r requirements.txt
```

</details>

<details>
<summary><h2>Pre-commit</h2></summary>

This project uses [pre-commit](https://pre-commit.com/) to run code formatting & linting checks before each commit. To install the pre-commit hooks, run:

```bash
pre-commit install
```

To run checks manually on all files:

```bash
pre-commit run --all-files --verbose
```

</details>

<details>
<summary><h2>Strava Integration</h2></summary>

Relevant links: [Strava Developers landing page](https://developers.strava.com/), [API reference](https://developers.strava.com/docs/reference/).

1. Create a new application on the [Strava API settings page](https://www.strava.com/settings/api) to get a `client_id` & a `client_secret`.
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

1. Set `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, & `STRAVA_REFRESH_TOKEN` appropriately in `.env`.

</details>

<details>
<summary><h2>Google Integrations</h2></summary>

I decided to create separate Google Cloud Platform projects for the Google Sheets & Google Calendar integrations. Mostly to keep privileges separate, but also just a style choice.

### Integrations for strava_to_pfitz_gsheet.py

1. Create a new Google Cloud Platform project to manage the connections used by `strava_to_pfitz_gsheet.py`. I chose to name mine "Strava to Pfitz GSheet".

1. Enable the Google Sheets & Google Drive APIs for this new project.

1. Under IAM & Admin > Service accounts, create a new service account for the project.

1. Create & download a new JSON key for this new service account. Save in `credentials/`. Set the `GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH` in `.env` to the full path (i.e. `realpath credentials/{FILENAME}.json`) of the JSON file.

1. Locate the Google Sheet you want to modify with the `strava_to_pfitz_gsheet.py` script. Copy the spreadsheet ID from the URL (the string between `/d/` & `/edit`, e.g. `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`). Set `GOOGLE_SHEETS_SPREADSHEET_ID` in `.env` to this ID.

1. Add service account email address to sheet with the `Editor` role.

### Integrations for strava_to_gcal.py

1. Create a new Google Cloud Platform project to manage connections used by `strava_to_gcal.py`. I chose to name mine "Strava to GCal".

1. Enable the Google Calendar API for this new project.

1. Following the [Google Calendar API Python Quickstart](https://developers.google.com/calendar/api/quickstart/python) instructions:

   1. Under the [Google Auth platform > Clients page](https://console.cloud.google.com/auth/clients), create a new OAuth 2.0 Client ID. Set the application type to "Desktop app".

   1. Download the credentials JSON & save in this repo. Set the `GOOGLE_CALENDAR_JSON_CREDENTIALS_FULL_PATH` in `.env` to the full path (i.e. `realpath credentials/{FILENAME}.json`) of the JSON file.

   1. Don't run script yet, finish rest of setup instructions. But note that on first run, you'll be redirected to authenticate with Google. A `strava-to-gcal-token.json` file will then automatically be created in `credentials/`, so ensure that you run from project root.

      1. Note: if there are any issues with the Google authentication flow, try visiting the URL in incognito mode.

1. Set the `GOOGLE_CALENDAR_STRAVA_CALENDAR_ID` in `.env` to the ID of the Google Calendar you want to add events to. If set to your gmail address, events will be added to your primary calendar. But it's preferable to create a dedicated calendar & use the `*@group.calendar.google.com` ID. This ID can be found on the calendar settings page in Google Calendar.

</details>

<details>
<summary><h2>ntfy.sh Integration</h2></summary>

[ntfy.sh](https://ntfy.sh/) is a simple pub/sub notification service that sends phone push notifications. The Strava scripts use it to notify you when they complete successfully or fail with an error.

1. Create a new topic on ntfy.sh. Your topic URL will be `https://ntfy.sh/{YOUR_TOPIC_NAME}`.

1. Set the `NTFY_TOPIC_URL` in `.env` to your full topic URL (e.g., `NTFY_TOPIC_URL=https://ntfy.sh/{YOUR_TOPIC_NAME}`).

1. Subscribe to your topic on your phone:
   - Install the ntfy app ([iOS](https://apps.apple.com/us/app/ntfy/id1625396347) or [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy))
   - Subscribe to your topic URL
   - You should now receive notifications when scripts run

</details>
