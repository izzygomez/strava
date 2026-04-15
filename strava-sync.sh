#!/bin/zsh

# Convenience script to run all Strava sync scripts in sequence.
# Usage: ./strava-sync.sh [SCRIPT_FLAGS...]
# Forwards all flags supported by the underlying Python scripts, including:
# --force-refresh, --notify-all, --start-date, --end-date, --timezone
# If --start-date/--end-date/--timezone are omitted, defaults below are used.

set -e # Exit on any error

# Resolve the repo root from the script's location (works even when invoked via PATH)
STRAVA_DIR="${0:A:h}"

# Training block dates for NYC United Half Marathon '26 Pfitz training plan.
START_DATE_GSHEET="2025-12-22"
END_DATE_GSHEET="2026-03-29"
# Dynamic last-30-days window (includes today).
START_DATE_GCAL="$(date -v-30d +%Y-%m-%d)"
END_DATE_GCAL="$(date +%Y-%m-%d)"
TIMEZONE="LOCAL"

# Set defaults first; any user-provided args later in "$@" override these.
default_args_gsheet=(
    --start-date "$START_DATE_GSHEET"
    --end-date "$END_DATE_GSHEET"
    --timezone "$TIMEZONE"
)
default_args_gcal=(
    --start-date "$START_DATE_GCAL"
    --end-date "$END_DATE_GCAL"
    --timezone "$TIMEZONE"
)

echo "🏃 Running all Strava sync scripts..."
# echo
# PYTHONPATH="$STRAVA_DIR" python -m scripts.strava_to_pfitz_gsheet "${default_args_gsheet[@]}" "$@"
echo
PYTHONPATH="$STRAVA_DIR" python -m scripts.strava_to_gcal "${default_args_gcal[@]}" "$@"
echo
echo "✅ All Strava sync scripts completed successfully!"
