#!/bin/zsh

# Convenience script to run all Strava sync scripts in sequence.
# Usage: ./strava_sync [--force-refresh | -f]

set -e # Exit on any error

# Resolve the repo root from the script's location (works even when invoked via PATH)
STRAVA_DIR="${0:A:h}"

# Training block dates (NYC United Half Marathon '26 Pfitz)
START_DATE="2025-12-22"
END_DATE="2026-03-29"
TIMEZONE="ET"

echo "🏃 Running all Strava sync scripts..."
echo
PYTHONPATH="$STRAVA_DIR" python -m scripts.strava_to_pfitz_gsheet --start-date "$START_DATE" --end-date "$END_DATE" --timezone "$TIMEZONE" "$@"
echo
PYTHONPATH="$STRAVA_DIR" python -m scripts.strava_to_gcal --start-date "$START_DATE" --end-date "$END_DATE" --timezone "$TIMEZONE" "$@"
echo
echo "✅ All Strava sync scripts completed successfully!"
