import gspread
from oauth2client.service_account import ServiceAccountCredentials


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
