# Strava Scripts

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Useful scripts for working with Strava data. A lot of functionality is based on my own personal use cases, but for the most part everything is written generically & with appropriate setup instructions to be adapted by others. Do note, though, that a lot of code here is still a 🚧 work-in-progress 🚧.

## Setup

See [SETUP.md](SETUP.md) for setup instructions.

## Usage

Assuming all setup steps have been completed, the following scripts are available for use.

### Convenience Script

For the most common use case of syncing to both Google Sheets & Google Calendar:

```shell
./strava_sync
```

This runs both `strava_to_pfitz_gsheet` & `strava_to_gcal` in sequence.

### Individual Scripts

When running scripts individually, you must specify the required date & timezone arguments.

#### strava_to_pfitz_gsheet.py

```shell
python -m scripts.strava_to_pfitz_gsheet --start-date {YYYY-MM-DD} --end-date {YYYY-MM-DD} --timezone {ET, PT, LOCAL, ...}
```

Script to convert Strava activities into clickable links in Google Sheets tracking a Pfitzinger training plan. For an example of what this script does, see the rightmost column of [izzy.gg/vancouver25](https://izzy.gg/vancouver25).

#### strava_to_gcal.py

```shell
python -m scripts.strava_to_gcal --start-date {YYYY-MM-DD} --end-date {YYYY-MM-DD} --timezone {ET, PT, LOCAL, ...}
```

Script to create Google Calendar events for Strava activities on specified calendar.

#### Everything else in scripts/

`python -m scripts.{script_name}`

Misc tasks that are personalized to my own use case. Not recommended for general use.

### Command line flags

Scripts called by `./strava_sync` support the following flags:

#### `--force-refresh`/`-f`

Strava API results are cached locally for 1 hour. The cache is automatically used when the requested date range falls within what's already cached.

Use the `--force-refresh`/`-f` flag to bypass the cache, fetch fresh data from Strava, & overwrite the cache:

```shell
./strava_sync --force-refresh
python -m scripts.strava_to_gcal --start-date {YYYY-MM-DD} --end-date {YYYY-MM-DD} --timezone ET -f
```

## TODOs

- Write script to automatically text me ~1 hr after running activity upload if I didn't specify gear (i.e. shoes).
- Figure out how to automatically trigger scripts when new activities are uploaded to Strava using webhooks.
- Add cmd line flag for skipping ntfy.sh notifications. Or make default behavior to not send notifications unless error, current behavior can be set by a flag.
- Add cmd line flag for dry run mode.
