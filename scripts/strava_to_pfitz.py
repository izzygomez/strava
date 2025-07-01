from datetime import datetime

import gspread
from dateutil import parser

from services import google_sheets_api, strava_api
from utils.load_env import (
    GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH,
    GOOGLE_SHEETS_SHEET_NAME,
    STRAVA_CLIENT_ID,
    STRAVA_CLIENT_SECRET,
    STRAVA_REFRESH_TOKEN,
)


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
                emoji = strava_api.get_emoji_for_sport_type(activity["sport_type"])
                text = f"{emoji} • {activity['name']}"
                url = strava_api.get_activity_url(activity["id"])
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
        print(f"\nUpdated {len(requests)} cells in the 'Strava Links' column.")


if __name__ == "__main__":
    access_token = strava_api.get_strava_access_token(
        STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
    )

    print("\nRunning Strava to Pfitz script...")

    # These are currently set to beginning & end dates for the NYC '25 Marathon
    # Pfitz training block.
    start_date = datetime(2025, 6, 30)
    end_date = datetime(2025, 12, 7)
    all_activities = strava_api.get_strava_activities(
        access_token, start_date, end_date, log=True
    )

    # Connect to the Google Sheet
    # Credentials file that was downloaded from Google Developer Console after creating
    # a new project, enabling the Google Sheets API, & creating a service account.
    sheet = google_sheets_api.connect_to_google_sheets(
        GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH,
        GOOGLE_SHEETS_SHEET_NAME,
    )

    # Find the 'Strava Links' & 'Date' header cell locations
    strava_column, strava_row = google_sheets_api.find_cell_index(sheet, "Strava Links")
    date_column, date_row = google_sheets_api.find_cell_index(sheet, "Date")
    strava_a1 = gspread.utils.rowcol_to_a1(strava_row, strava_column)
    date_a1 = gspread.utils.rowcol_to_a1(date_row, date_column)
    # print(f"'Strava Links' header is at {strava_a1}")  # DEBUG
    # print(f"'Date' header is at {date_a1}")  # DEBUG

    # Ensure the date column and strava column headers are on the same row
    if date_row != strava_row:
        raise ValueError("'Date' and 'Strava Links' headers are not on the same row")

    # Update the 'Strava Links' column with Strava activity links
    update_strava_links(sheet, strava_column, strava_row, date_column, all_activities)
