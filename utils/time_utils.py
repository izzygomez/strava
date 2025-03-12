from datetime import datetime, timedelta

# Useful datetime-related functions


def izzys_strava_start_date() -> datetime:
    """
    I believe first Strava activity was on September 10, 2018, but it doesn't
    hurt to set this a bit earlier.
    """
    return datetime(2018, 9, 1)


def n_days_from_today(n: int) -> datetime:
    return datetime.now() + timedelta(days=n)


def n_days_ago_from_today(n: int) -> datetime:
    return datetime.now() - timedelta(days=n)
