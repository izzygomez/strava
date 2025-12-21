import traceback
from datetime import datetime

from collections import defaultdict
import gspread
from dateutil import parser

from services import google_sheets_api, ntfy_api, strava_api
from utils.load_env import (
    GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH,
    GOOGLE_SHEETS_SHEET_NAME,
    NTFY_TOPIC_URL,
    STRAVA_CLIENT_ID,
    STRAVA_CLIENT_SECRET,
    STRAVA_REFRESH_TOKEN,
)


def update_strava_links(sheet, strava_column, strava_row, date_column, activities):
    """
    Update cells under 'Strava Links' with multiple Strava activity links, using
    a single batch_update call.
    """
    date_cells = sheet.col_values(date_column)
    strava_cells = sheet.col_values(strava_column)
    spreadsheet = sheet.spreadsheet
    requests = []
    cells_skipped = 0

    # Group activities by date for efficiency
    # format: { date -> [{"text": <cell_text>, "url": <url>}, ...] }
    activities_by_date = defaultdict(list)
    for activity in activities:
        activity_date = datetime.strptime(
            activity["start_date_local"][:10], "%Y-%m-%d"
        ).date()

        emoji = strava_api.get_emoji_for_sport_type(activity["sport_type"])
        cell_text = f"{emoji} • {activity['name']}"
        url = strava_api.get_activity_url(activity["id"])
        activities_by_date[activity_date].append({"text": cell_text, "url": url})

    # Create update requests for each cell, which will be batched at the end.
    # Solution for multiple hyperlinks per cell inspired by this:
    # https://stackoverflow.com/a/77312815
    for i in range(strava_row, len(date_cells)):
        date_value = date_cells[i]
        if not date_value:
            continue
        try:
            parsed_date = parser.parse(date_value).date()
        except ValueError:
            print(f"Skipping unrecognized date format: {date_value}")
            continue

        # Get activities for this date
        activities_for_date = activities_by_date.get(parsed_date, [])

        # Only update if there are activities for this date
        if activities_for_date:
            cell_text = "\n".join([a["text"] for a in activities_for_date])

            # Check if the cell already has this text value.
            # NOTE: this is not checking the formatting of the cell, i.e. the
            # hyperlinks, so we may skip updating a cell if the text is the same
            # but the hyperlink content or format is different.
            existing_value = strava_cells[i] if i < len(strava_cells) else ""
            if existing_value == cell_text:
                cells_skipped += 1
                continue

            new_cell_content = [
                {
                    "values": [
                        {
                            "userEnteredValue": {"stringValue": cell_text},
                            "textFormatRuns": [
                                {
                                    "format": {"link": {"uri": a["url"]}},
                                    # This is necessary to ensure the hyperlink
                                    # for each individual activity starts in the
                                    # right index. Otherwise, the hyperlinks
                                    # will overlap & all links won't be properly
                                    # clickable.
                                    "startIndex": cell_text.find(a["text"]),
                                }
                                for a in activities_for_date
                            ],
                        }
                    ]
                }
            ]
            requests.append(
                {
                    "updateCells": {
                        "rows": new_cell_content,
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

    # Batch update the cells
    if requests:
        spreadsheet.batch_update({"requests": requests})

    print(
        f"Updated {len(requests)} cells & "
        f"skipped {cells_skipped} existing cells — "
        f"out of {len(activities)} activities."
    )

    return {
        "updated": len(requests),
        "skipped": cells_skipped,
        "total_activities": len(activities),
    }


if __name__ == "__main__":
    try:
        access_token = strava_api.get_strava_access_token(
            STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
        )

        print("📊 Syncing Strava activities to Pfitz training plan Google Sheet...")
        # These are currently set to beginning & end dates for the NYC '25 Marathon
        # Pfitz training block.
        start_date = datetime(2025, 6, 30)
        end_date = datetime(2026, 1, 1)
        # remember that end_date is non-inclusive, so make sure end_date is
        # one more than plan's actual end date
        print()
        sorted_activities = strava_api.get_sorted_strava_activities(
            access_token, start_date, end_date
        )

        # Connect to the Google Sheet
        # Credentials file that was downloaded from Google Developer Console after creating
        # a new project, enabling the Google Sheets API, & creating a service account.
        sheet = google_sheets_api.connect_to_google_sheets(
            GOOGLE_SHEETS_JSON_KEYFILE_FULL_PATH,
            GOOGLE_SHEETS_SHEET_NAME,
        )

        # Find the 'Strava Links' & 'Date' header cell locations
        strava_column, strava_row = google_sheets_api.find_cell_index(
            sheet, "Strava Links"
        )
        date_column, date_row = google_sheets_api.find_cell_index(sheet, "Date")
        strava_a1 = gspread.utils.rowcol_to_a1(strava_row, strava_column)
        date_a1 = gspread.utils.rowcol_to_a1(date_row, date_column)
        # print(f"'Strava Links' header is at {strava_a1}")  # DEBUG
        # print(f"'Date' header is at {date_a1}")  # DEBUG

        # Ensure the date column and strava column headers are on the same row
        if date_row != strava_row:
            raise ValueError(
                "'Date' and 'Strava Links' headers are not on the same row"
            )

        # Update the 'Strava Links' column with Strava activity links
        print()
        stats = update_strava_links(
            sheet, strava_column, strava_row, date_column, sorted_activities
        )

        # Send success notification only if changes were made
        if stats["updated"] > 0:
            title = "Strava to Pfitz GSheet - Success"
            message = (
                f"Successfully synced Strava activities to Pfitz training sheet.\n\n"
                f"Dates: [{start_date.strftime('%m/%d/%Y')}, "
                f"{end_date.strftime('%m/%d/%Y')})\n"
                f"Cells updated: {stats['updated']}\n"
                f"Cells skipped: {stats['skipped']}\n"
                f"Activities processed: {stats['total_activities']}"
            )
            print()
            ntfy_api.send_notification(
                NTFY_TOPIC_URL,
                message,
                title=title,
                priority="default",
                tags=["white_check_mark"],
            )
        else:
            print()
            print("Skipping ntfy.sh notification, no changes were made")
    except Exception as e:
        print()
        print("Strava to Pfitz GSheet script failed. Sending failure notification")
        # Send failure notification
        title = "Strava to Pfitz GSheet - Failed"
        error_trace = traceback.format_exc()
        message = f"Script failed with error:\n\n{str(e)}\n\n{error_trace}"
        print()
        ntfy_api.send_notification(
            NTFY_TOPIC_URL, message, title=title, priority="high", tags=["x", "warning"]
        )
        # Re-raise the exception so the script still exits with an error code
        raise
