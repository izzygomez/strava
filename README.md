# Strava Scripts

Repo to contain useful scripts for interacting with my Strava data.

## Usage

`strava2pfitz.py`

- Create & fill in `.env` file, & download Google Sheets JSON keyfile.
- Install the required dependencies: `pip install -r requirements.txt`
- Run: `python strava2pfitz.py`

For an example of how this script is used, see the rightmost column of [izzygomez.com/r/erie2024](https://izzygomez.com/r/erie2024).

## TODOs

- Write script to automatically text me ~1 hr after running activity upload if I didn't specify gear (i.e. shoes).
