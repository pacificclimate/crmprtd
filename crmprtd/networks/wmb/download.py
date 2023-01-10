"""Downloads meteorological data from BC's Wildfire Management Branch

The BC Wildfire Service (FLNRORD-WMB) posts a rolling window (one day)
of weather data once every hour.

It is recommended to run this script once per hour to collect all
available data (plus, presumably duplicate data from the last run),
supplemented with aggressive monitoring and alerting for errors. If
the script is run less than daily or there are any outages lasting
greater than 24 hours, you will miss data.
"""

# Standard module
from typing import List
import os
import logging.config
import ftplib
import sys
from tempfile import SpooledTemporaryFile
from argparse import ArgumentParser

# Local
from crmprtd.download_utils import retry, ftp_connect
from crmprtd.download_utils import FTPReader, extract_auth
from crmprtd import (
    setup_logging,
    add_common_auth_arguments,
    get_version,
)

log = logging.getLogger(__name__)


def download(username, password, auth_fname, auth_key, ftp_server, ftp_file):
    log.info("Starting WMB rtd")

    auth_yaml = open(auth_fname, "r").read() if auth_fname else None
    auth = extract_auth(username, password, auth_yaml, auth_key)

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(WMBFTPReader, ftp_server, ftp_file, log, auth)

        with SpooledTemporaryFile(
            max_size=int(os.environ.get("CRMPRTD_MAX_CACHE", 2**20)), mode="r+"
        ) as tempfile:

            def callback(line):
                tempfile.write("{}\n".format(line))

            for filename in ftpreader.filenames:
                log.info("Downloading %s", filename)
                ftpreader.connection.retrlines("RETR {}".format(filename), callback)
            tempfile.seek(0)
            for line in tempfile.readlines():
                sys.stdout.buffer.write(line.encode("utf-8"))

    except Exception as e:
        log.exception("Unable to process ftp")


class WMBFTPReader(FTPReader):
    """Glue between the FTP_TLS class methods (which are callback based)
    and the csv.DictReader class (which is iteration based)
    """

    def __init__(self, host, user, password, filename, log=None):
        self.filenames = [filename]

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            return ftplib.FTP_TLS(host, user, password)

        self.connection = ftp_connect_with_retry(host, user, password)


def main(
    arglist: List[str] = None, parent_parser: ArgumentParser = None
) -> None:  # pragma: no cover
    """Download CLI function for BC Hydro

    Side effect: Sends downloaded XML files to STDOUT.

    :param arglist: Argument list (for testing; default is to parse from sys.argv).
    :param parent_parser: Argument parser common to all network downloads.
    """
    desc = globals()["__doc__"]

    parser = ArgumentParser(parents=[parent_parser], description=desc)
    add_common_auth_arguments(parser)
    parser.add_argument(
        "-f",
        "--ftp_server",
        default="BCFireweatherFTPp1.nrs.gov.bc.ca",
        help="Full uri to Wildfire Management Branch's ftp server",
    )
    parser.add_argument(
        "-F",
        "--ftp_file",
        default="HourlyWeatherAllFields_WA.txt",
        help="Filename to open on the Wildfire Management Branch's ftp site",
    )
    args = parser.parse_args(arglist)

    if args.version:
        print(get_version())
        return

    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd.networks.wmb",
    )

    download(
        args.username,
        args.password,
        args.auth_fname,
        args.auth_key,
        args.ftp_server,
        args.ftp_file,
    )


if __name__ == "__main__":
    main()
