# Strava scripts

Repo to contain useful scripts for interacting with my Strava data.

## Usage

`strava2pfitz.py`

- Create & fill in `.env` file, & download Google Sheets JSON keyfile.
- Install the required dependencies: `pip install -r requirements.txt`.
- Run: `python strava2pfitz.py`

## TODOs

- Split up `strava2pfitz.py` into `strava.py`, `google_sheets.py`, etc.
- Write script to automatically text me ~1 hr after running activity upload if I didn't specify gear (i.e. shoes).
