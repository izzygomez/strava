# Strava Scripts

Useful scripts for working with Strava data. A lot of functionality is based on my own personal use cases, but for the most part everything is written generically & with appropriate setup instructions to be adapted by others.

Do note, though, that a lot of code here is still a 🚧 work-in-progress 🚧.

## Setup

See [SETUP.md](SETUP.md) for setup instructions.

## Usage

Assuming all setup steps have been completed, the following scripts are available for use:

#### strava_to_pfitz_gsheet.py

`python -m scripts.strava_to_pfitz_gsheet`

Script to convert Strava activities into clickable links in Google Sheets tracking a Pfitzinger training plan. For an example of what this script does, see the rightmost column of [izzy.gg/r/vancouver2025](https://izzy.gg/r/vancouver2025).

#### strava_to_gcal.py

`python -m scripts.strava_to_gcal`

Script to create Google Calendar events for Strava activities on specified calendar.

#### Everything else in scripts/

Misc tasks that are personalized to my own use case. Not recommended for general use.

## TODOs

- Write script to automatically text me ~1 hr after running activity upload if I didn't specify gear (i.e. shoes).
- Figure out how to automatically trigger scripts when new activities are uploaded to Strava.
- Finish setting up pre-commit
