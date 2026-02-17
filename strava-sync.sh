#!/bin/zsh

# Convenience script to run all Strava sync scripts in sequence.
# Usage: ./strava-sync.sh [SCRIPT_FLAGS...]
# Forwards all flags supported by the underlying Python scripts, including:
# --force-refresh, --notify-all, --start-date, --end-date, --timezone
# If --start-date/--end-date/--timezone are omitted, defaults below are used.

set -e # Exit on any error

# Resolve the repo root from the script's location (works even when invoked via PATH)
STRAVA_DIR="${0:A:h}"

# Training block dates (NYC United Half Marathon '26 Pfitz)
START_DATE="2025-12-22"
END_DATE="2026-03-29"
TIMEZONE="ET"

# Set defaults first; any user-provided args later in "$@" override these.
default_args=(
    --start-date "$START_DATE"
    --end-date "$END_DATE"
    --timezone "$TIMEZONE"
)

echo "🏃 Running all Strava sync scripts..."
echo
PYTHONPATH="$STRAVA_DIR" python -m scripts.strava_to_pfitz_gsheet "${default_args[@]}" "$@"
echo
PYTHONPATH="$STRAVA_DIR" python -m scripts.strava_to_gcal "${default_args[@]}" "$@"
echo
echo "✅ All Strava sync scripts completed successfully!"
