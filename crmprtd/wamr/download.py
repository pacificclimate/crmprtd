"""Downloads the BC Weather and Air Monitoring and Reporting (WAMR) data.

The BC Ministry of Environment, Air Quality Network (AQN) (also known
as WAMR) branch posts a rolling window (one month) of weather data
once every day.

It is recommended to run this script once per one or two weeks to
collect all available data (plus, presumably some duplicate data from
the last run). If the script is run less than once per month, you will
miss data.
"""

import ftplib
import logging
import os
import sys

from tempfile import SpooledTemporaryFile
from argparse import ArgumentParser

# Local
from crmprtd.download import retry, ftp_connect
from crmprtd.download import FTPReader
from crmprtd import logging_args, setup_logging


log = logging.getLogger(__name__)


def download(ftp_server, ftp_dir, output_buffer=sys.stdout.buffer):
    """Executes the first stage of the data processing pipeline.

    Downloads the data, according to the download arguments
    provided (generally from the command line) and outputs the data
    to stdout.
    """
    log.info("Starting WAMR rtd")

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(WAMRFTPReader, ftp_server, ftp_dir, log)

        with SpooledTemporaryFile(
            max_size=int(os.environ.get("CRMPRTD_MAX_CACHE", 2 ** 20)), mode="r+"
        ) as tempfile:

            for filename in ftpreader.filenames:

                def callback(line):
                    tempfile.write("{}\n".format(line))

                log.info("Downloading %s", filename)
                ftpreader.connection.retrlines("RETR {}".format(filename), callback)

            tempfile.seek(0)
            for line in tempfile.readlines():
                output_buffer.write(line.encode("utf-8"))

    except Exception:
        log.exception("Unable to process ftp")


class WAMRFTPReader(FTPReader):
    """Glue between the FTP class methods (which are callback based)
    and the csv.DictReader class (which is iteration based)
    """

    def __init__(self, host, user, password, data_path, log=None):
        self.filenames = []

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            con = ftplib.FTP(host)
            con.login(user, password)
            return con

        self.connection = ftp_connect_with_retry(host, user, password)

        def callback(line):
            self.filenames.append(line)

        self.connection.retrlines("NLST " + data_path, callback)


def main():
    desc = globals()["__doc__"]
    parser = ArgumentParser(description=desc)
    parser.add_argument(
        "-f",
        "--ftp_server",
        default="ftp.env.gov.bc.ca",
        help=(
            "Full hostname of Water and Air Monitoring and " "Reporting's ftp server"
        ),
    )
    parser.add_argument(
        "-F",
        "--ftp_dir",
        default=("pub/outgoing/AIR/Hourly_Raw_Air_Data/" "Meteorological/"),
        help="FTP Directory containing WAMR's data files",
    )
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd.wamr",
    )

    download(args.ftp_server, args.ftp_dir)


if __name__ == "__main__":
    main()
