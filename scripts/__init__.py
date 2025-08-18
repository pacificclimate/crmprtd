
from datetime import datetime, timedelta, timezone
import os


def add_bulk_args(parser):
    """
    Add common arguments for bulk download/processing scripts.
    """

    parser.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help=(
            "directory in which to operate, downloaded files will be saved here,"
            " processing will pull from here"
        ),
    )
    parser.add_argument(
        "-N",
        "--network",
        dest="network",
        help="The network from which the data is coming from",
    )


def add_time_range_args(parser):
    """
    Add common time range arguments for bulk scripts.

    Args:
        start_required: Whether the start date should be required
        frequency_required: Whether the frequency should be required
    """
    parser.add_argument(
        "-S",
        "--start_date",
        dest="stime",
        required=True,
        help=(
            "Start time (UTC) of range to process (format: '%%Y-%%m-%%d %%H:%%M:%%S'). "
            "Interpreted with strptime and rounded to the nearest hour."
        ),
    )
    parser.add_argument(
        "-E",
        "--end_date",
        dest="etime",
        default=datetime.now(timezone.utc),
        help=(
            "End time (UTC) of range to process (format: '%%Y-%%m-%%d %%H:%%M:%%S'). "
            "Interpreted with strptime and rounded to the nearest hour. Defaults to the current UTC time."
        ),
    )
    parser.add_argument(
        "-F",
        "--frequency",
        dest="frequency",
        required=True,
        choices=["daily", "hourly"],
        help="Frequency for bulk operations (daily or hourly), determines the timestep while looping through the time range",
    )

def ensure_log_directory(log_filename):
    """
    Ensure the log directory exists.
    
    Args:
        log_filename: The path to the log file.
    """
    if log_filename:
        log_dir = os.path.dirname(log_filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)