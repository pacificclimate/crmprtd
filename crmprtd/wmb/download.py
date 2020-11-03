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
import os
import logging
import logging.config
import ftplib
import sys
from tempfile import SpooledTemporaryFile
from argparse import ArgumentParser

# Local
from crmprtd.download import retry, ftp_connect
from crmprtd.download import FTPReader, extract_auth
from crmprtd import logging_args, setup_logging, common_auth_arguments

log = logging.getLogger(__name__)


def download(username, password, auth_fname, auth_key, ftp_server, ftp_file):
    log.info("Starting WMB rtd")

    auth_yaml = open(auth_fname, "r").read() if auth_fname else None
    auth = extract_auth(username, password, auth_yaml, auth_key)

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(WMBFTPReader, ftp_server, ftp_file, log, auth)

        with SpooledTemporaryFile(
            max_size=int(os.environ.get("CRMPRTD_MAX_CACHE", 2 ** 20)), mode="r+"
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


def main():
    desc = globals()["__doc__"]
    parser = ArgumentParser(description=desc)
    parser = logging_args(parser)
    parser = common_auth_arguments(parser)
    parser.add_argument(
        "-f",
        "--ftp_server",
        default="BCFireweatherFTPp1.nrs.gov.bc.ca",
        help=("Full uri to Wildfire Management Branch's ftp " "server"),
    )
    parser.add_argument(
        "-F",
        "--ftp_file",
        default="HourlyWeatherAllFields_WA.txt",
        help=("Filename to open on the Wildfire Management " "Branch's ftp site"),
    )
    args = parser.parse_args()

    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd.wmb",
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
