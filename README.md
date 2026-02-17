# Strava Scripts

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Useful scripts for working with Strava data. A lot of functionality is based on my own personal use cases, but for the most part everything is written generically & with appropriate setup instructions to be adapted by others. Do note, though, that a lot of code here is still a 🚧 work-in-progress 🚧.

## Setup

See [SETUP.md](SETUP.md) for setup instructions.

## Usage

After completing setup, you can use the following scripts & command-line flags.

<details>
<summary><h3>Combined Sync (Sheets + Calendar)</h3></summary>

Use this when you want to run both sync jobs in one command:

```shell
./strava-sync.sh
```

This runs `strava_to_pfitz_gsheet` & `strava_to_gcal` sequentially.

- All supported command-line flags are forwarded to both scripts.
- `--start-date`, `--end-date`, & `--timezone` are optional.
- If those three flags are omitted, `strava-sync.sh` uses its built-in defaults.

</details>

<details>
<summary><h3>Run Individual Scripts</h3></summary>

Use these commands when you only want one sync target.

#### strava_to_pfitz_gsheet.py

```shell
python -m scripts.strava_to_pfitz_gsheet --start-date {s} --end-date {e} --timezone {tz} [OTHER_FLAGS...]
```

Converts Strava activities into clickable links in the Google Sheets training log. Requires `--start-date`, `--end-date`, & `--timezone`. For an example, see the rightmost column of [izzy.gg/vancouver25](https://izzy.gg/vancouver25).

#### strava_to_gcal.py

```shell
python -m scripts.strava_to_gcal --start-date {s} --end-date {e} --timezone {tz} [OTHER_FLAGS...]
```

Creates Google Calendar events for Strava activities on the configured calendar. Requires `--start-date`, `--end-date`, & `--timezone`.

#### Other scripts in scripts/

`python -m scripts.{script_name}`

Misc tasks that are personalized to my own use case. Not recommended for general use.

</details>

<details>
<summary><h3>Command-line flags</h3></summary>

Scripts called by `./strava-sync.sh` support the following flags:

| Flag              | Short | Value                                  | Description                                                                                        |
| ----------------- | ----- | -------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `--start-date`    | -     | `YYYY-MM-DD`                           | Start date of the sync range. If omitted, `strava-sync.sh` uses its built-in default.              |
| `--end-date`      | -     | `YYYY-MM-DD`                           | End date of the sync range. If omitted, `strava-sync.sh` uses its built-in default.                |
| `--timezone`      | -     | `LOCAL`, `ET`, `PT`, `CT`, `MT`, `UTC` | Timezone used when parsing date arguments. If omitted, `strava-sync.sh` uses its built-in default. |
| `--force-refresh` | `-f`  | -                                      | Bypass the Strava activity cache & fetch fresh data from the API.                                  |
| `--notify-all`    | -     | -                                      | Send ntfy.sh success notifications in addition to failure notifications.                           |

</details>

<details>
<summary><h2>TODOs</h2></summary>

- Write script to automatically text me ~1 hr after running activity upload if I didn't specify gear (i.e. shoes).
- Figure out how to automatically trigger scripts when new activities are uploaded to Strava using webhooks.
- Add command-line flag for dry run mode.
- Add rate-limiting to Strava API calls to gracefully handle 429 errors.
</details>
