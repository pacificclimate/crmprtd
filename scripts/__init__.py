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


def add_time_range_args(parser, start_required=False, frequency_required=False):
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
        required=start_required,
        help=(
            "Start time (UTC) of range to process (format: '%%Y-%%m-%%d %%H:%%M:%%S'). "
            "Interpreted with strptime and rounded to the nearest hour."
        ),
    )
    parser.add_argument(
        "-E",
        "--end_date",
        dest="etime",
        help=(
            "End time (UTC) of range to process (format: '%%Y-%%m-%%d %%H:%%M:%%S'). "
            "Interpreted with strptime and rounded to the nearest hour."
        ),
    )
    parser.add_argument(
        "-F",
        "--frequency",
        dest="frequency",
        required=frequency_required,
        choices=["daily", "hourly"],
        help="Frequency for bulk operations (daily or hourly)",
    )
