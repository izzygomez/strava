import argparse


def add_common_sync_flags(arg_parser: argparse.ArgumentParser) -> None:
    """
    Add shared CLI flags used by Strava sync scripts.
    """
    arg_parser.add_argument(
        "-f",
        "--force-refresh",
        action="store_true",
        help="Bypass Strava API cache & fetch fresh data",
    )
    arg_parser.add_argument(
        "-s",
        "--start-date",
        required=True,
        help="Start date in YYYY-MM-DD format",
    )
    arg_parser.add_argument(
        "-e",
        "--end-date",
        required=True,
        help="End date in YYYY-MM-DD format",
    )
    arg_parser.add_argument(
        "-t",
        "--timezone",
        required=True,
        help="Timezone alias (LOCAL, ET, PT, CT, MT, UTC)",
    )
    arg_parser.add_argument(
        "-n",
        "--notify-all",
        action="store_true",
        help="Send ntfy.sh notifications for success & failures. By default, only failures send notifications.",
    )


def build_sync_arg_parser(description: str) -> argparse.ArgumentParser:
    """
    Create an ArgumentParser preloaded with shared sync flags.
    """
    arg_parser = argparse.ArgumentParser(description=description)
    add_common_sync_flags(arg_parser)
    return arg_parser
