from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# Common timezone constants
UTC = timezone.utc
EASTERN = ZoneInfo("America/New_York")  # ET (EST/EDT)
PACIFIC = ZoneInfo("America/Los_Angeles")  # PT (PST/PDT)
LOCAL_TZ = datetime.now().astimezone().tzinfo  # System's local timezone


def _local_start_of_day(dt: datetime) -> datetime:
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
    return _local_start_of_day(datetime(2018, 9, 1, tzinfo=EASTERN))


def today() -> datetime:
    """Return start of today (local timezone) as a UTC datetime."""
    return _local_start_of_day(datetime.now())


def n_days_from_today(n: int) -> datetime:
    """Return start of n days from today (local tz) as UTC datetime."""
    return today() + timedelta(days=n)


def n_days_ago_from_today(n: int) -> datetime:
    """Return start of n days ago from today (local tz) as UTC datetime."""
    return today() - timedelta(days=n)
