from datetime import datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo

# Common timezone constants
UTC = timezone.utc
EASTERN = ZoneInfo("America/New_York")  # ET (EST/EDT)
CENTRAL = ZoneInfo("America/Chicago")  # CT (CST/CDT)
MOUNTAIN = ZoneInfo("America/Denver")  # MT (MST/MDT)
PACIFIC = ZoneInfo("America/Los_Angeles")  # PT (PST/PDT)
LOCAL_TZ = datetime.now().astimezone().tzinfo  # System's local timezone

# Timezone aliases for CLI args
TIMEZONE_ALIASES = {
    "LOCAL": LOCAL_TZ,
    "ET": EASTERN,
    "CT": CENTRAL,
    "MT": MOUNTAIN,
    "PT": PACIFIC,
    "UTC": UTC,
}


def local_start_of_day(dt: datetime) -> datetime:
    """
    Return the start of the day (midnight) for the given datetime,
    in its timezone (or local if naive), then converted to UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LOCAL_TZ)
    # Normalize to start of day in the datetime's own timezone
    midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    # Convert to UTC for consistent comparisons
    return midnight.astimezone(UTC)


def izzys_strava_start_date() -> datetime:
    """
    I believe first Strava activity was on September 10, 2018, but it doesn't
    hurt to set this a bit earlier.
    """
    return local_start_of_day(datetime(2018, 9, 1, tzinfo=EASTERN))


def today() -> datetime:
    """Return start of today (local timezone) as a UTC datetime."""
    return local_start_of_day(datetime.now(LOCAL_TZ))


def n_days_from_today(n: int) -> datetime:
    """Return start of n days from today (local tz) as UTC datetime."""
    return today() + timedelta(days=n)


def n_days_ago_from_today(n: int) -> datetime:
    """Return start of n days ago from today (local tz) as UTC datetime."""
    return today() - timedelta(days=n)


def parse_timezone_arg(tz_str: str) -> tzinfo:
    """Parse timezone alias (ET, PT, LOCAL, etc.) into ZoneInfo."""
    tz = TIMEZONE_ALIASES.get(tz_str.upper())
    if not tz:
        valid = ", ".join(TIMEZONE_ALIASES.keys())
        raise ValueError(f"Invalid timezone: '{tz_str}'. Valid options: {valid}")
    return tz


def parse_date_arg(date_str: str, tz: tzinfo) -> datetime:
    """Parse YYYY-MM-DD string into timezone-aware datetime (start of day)."""
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=tz)
    except ValueError:
        raise ValueError(
            f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD (e.g., 2025-12-22)"
        )
    return local_start_of_day(parsed)
