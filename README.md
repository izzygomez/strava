# Strava Scripts

Useful scripts for working with Strava data. A lot of functionality is based on my own personal use cases, but for the most part everything is written generically & with appropriate setup instructions to be adapted by others.

Do note, though, that a lot of code here is still a 🚧 work-in-progress 🚧.

## Setup

See [SETUP.md](SETUP.md) for setup instructions.

## Usage

Assuming all setup steps have been completed, the following scripts are available for use.

**Note:** All scripts send push notifications via [ntfy.sh](https://ntfy.sh/) when they complete (success or failure) with relevant stats & error details. See [SETUP.md](SETUP.md) for configuration.

### Convenience Script

For the most common use case of syncing to both Google Sheets & Google Calendar:

```bash
./strava_sync
```

This runs both `strava_to_pfitz_gsheet` & `strava_to_gcal` in sequence.

### Individual Scripts

#### strava_to_pfitz_gsheet.py

`python -m scripts.strava_to_pfitz_gsheet`

Script to convert Strava activities into clickable links in Google Sheets tracking a Pfitzinger training plan. For an example of what this script does, see the rightmost column of [izzy.gg/vancouver25](https://izzy.gg/vancouver25).

#### strava_to_gcal.py

`python -m scripts.strava_to_gcal`

Script to create Google Calendar events for Strava activities on specified calendar.

#### Everything else in scripts/

Misc tasks that are personalized to my own use case. Not recommended for general use.

## Pre-commit

This repo uses [`pre-commit`](https://pre-commit.com/) to automatically format & lint files before they are committed, & also as part of the required checks before a PR can be merged via [pre-commit.ci](https://pre-commit.ci/). See `.pre-commit-config.yaml` for configuration details.

## TODOs

- Write script to automatically text me ~1 hr after running activity upload if I didn't specify gear (i.e. shoes).
- Figure out how to automatically trigger scripts when new activities are uploaded to Strava.
