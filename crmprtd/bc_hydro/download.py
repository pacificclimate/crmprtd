""" Downloads data from BC hyrdo

BC Hydro posts a rolling window (3 months) observing hourly data
once a week. Data is in txt files.

It is recommended to run this script once a week to collect
updated available data, supplemented with monitoring and alerting
for errors. If the script is run less than once every 3 months
you will miss data.
"""

import pysftp
import logging
import os
import sys
import re
from zipfile import ZipFile
from argparse import ArgumentParser
from datetime import date, timedelta, datetime
from functools import partial
from tempfile import mkstemp
from contextlib import contextmanager

from dateutil import relativedelta
import dateutil.parser

from crmprtd import logging_args, setup_logging

log = logging.getLogger(__name__)


def download(username, gpg_private_key, ftp_server, ftp_dir, start_date, end_date):

    # Connect FTP server and retrieve directory
    try:
        connection = pysftp.Connection(
            ftp_server, username=username, private_key=gpg_private_key
        )

    except Exception:
        log.exception("Invalid ftp authentication")

    # Downloads files to temporary directory then prints contents to stdout
    try:
        """Walktree has 4 required arguements, 3 of which are
        functions with form: func(filename)"""
        no_op = lambda x: None  # noqa: E731
        callback = partial(
            download_relevant_bch_zipfiles, start_date, end_date, connection
        )
        connection.walktree(ftp_dir, callback, no_op, no_op)

    except IOError:
        log.exception("Unable to download or open some files")


@contextmanager
def temp_filename(suffix=".zip"):
    """Return the name of temporary file and ensure that it gets removed
    at the end of the context block.  This offers a slightly different
    API than anything in the tempfile module, in that it returns a
    *name* (not an open file object) and cleans it up at the end.
    """
    _, fname = mkstemp(suffix)
    yield fname
    if os.path.exists(fname):
        os.remove(fname)


# Add files within date range to tmp dir
def download_relevant_bch_zipfiles(start_date, end_date, connection, remote_filename):
    """sftp callback for walking the FTP tree and downloading data

    This function is a little overloaded in its responsibilities as a
    consequence of the pysftp API (which only allows you to provide a
    single callback function with no return value).

    Given a remote_filename and a data range, this function will
    filter out files that don't match the date patterns that we
    expect, download those that fall within the range, and print the
    output to standard output.

    """
    pattern = r"PCIC_BCHhourly_([0-9]{6}).zip"
    match = re.search(pattern, remote_filename)

    if not match:
        return

    file_time = datetime.strptime(match.group(1), "%y%m%d")

    if file_time < start_date or file_time > end_date:
        return

    with temp_filename() as file_path:
        connection.get(remote_filename, file_path)

        with ZipFile(file_path, "r") as zip_file:
            for name in zip_file.namelist():
                txt_file = zip_file.open(name)
                sys.stdout.buffer.write(txt_file.read())


def main():  # pragma: no cover
    desc = globals()["__doc__"]
    parser = ArgumentParser(description=desc)
    parser = logging_args(parser)
    parser.add_argument(
        "-u", "--username", default="pcic", help=("Username for the ftp server ")
    )
    parser.add_argument(
        "-f",
        "--ftp_server",
        default="sftp2.bchydro.com",
        help=("Full uri to BC Hydro's ftp " "server"),
    )
    parser.add_argument(
        "-F",
        "--ftp_dir",
        default=("pcic"),
        help=("FTP Directory containing BC hydro's " "data files"),
    )
    parser.add_argument(
        "-S",
        "--ssh_private_key",
        required=True,
        help=("Path to file with SSH private key"),
    )
    end = datetime.now()
    start = end - relativedelta.relativedelta(months=1)
    parser.add_argument(
        "-s",
        "--start_date",
        default=start,
        type=dateutil.parser.parse,
        help=(
            "Optional start time to use for downloading "
            "(interpreted with dateutil.parser.parse). "
            "Defaults to one month prior to now."
        ),
    )
    parser.add_argument(
        "-e",
        "--end_date",
        default=end,
        type=dateutil.parser.parse,
        help=(
            "Optional end time to use for downloading "
            "(interpreted with dateutil.parser.parse). "
            "Defaults to now."
        ),
    )
    args = parser.parse_args()

    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd.bc_hydro",
    )

    download(
        args.username,
        args.ssh_private_key,
        args.ftp_server,
        args.ftp_dir,
        args.start_date,
        args.end_date,
    )


if __name__ == "__main__":
    main()
