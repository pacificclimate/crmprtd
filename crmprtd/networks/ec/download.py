"""Downloads meteorological data from Environment and Climate Change Canada.

Environment and Climate Change Canada (ECCC) post two sets of XML
files containing weather observations, one for daily variables
(e.g. daily high temperature) and one for hourly variables. They post
a new file every hour or day, depending on the temporal resolution.
Each new file containing only the data for that time range. Data is
retained on dd.weather.gc.ca for 30 days and on
hpfx.collab.science.gc.ca for 90 days.

It is recommended to run this script once per hour with the "-F
hourly" flag or once per day with the "-F daily" flag. There is
sufficient overlap between the time resolution and the historical data
available that only the significant outtages (over a quarter) would
result in data loss.

"""

# Standard module
from typing import List
import sys
import logging.config
from datetime import datetime, timedelta, timezone
from argparse import ArgumentParser

# Local
from crmprtd.networks.ec import makeurl
from crmprtd import setup_logging
from crmprtd.download_utils import https_download, verify_date

log = logging.getLogger(__name__)


def download(time, frequency, province, language, baseurl):
    log.info("Starting EC rtd")

    try:
        # Determine time parameter
        deltat = timedelta(1 / 24.0) if frequency == "hourly" else timedelta(1)

        if time:
            time = verify_date(time, datetime.now(timezone.utc) - deltat, "time")
            log.info("Starting manual run " f"using timestamp {time}")
        else:
            # go back a day
            time = datetime.now(timezone.utc) - deltat
            log.info("Starting automatic run " f"using timestamp {time}")

        # Construct and download the xml
        url = makeurl(frequency, province, language, time, baseurl)

        scheme, _ = url.split(":", 1)
        https_download(url, scheme, log)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)


def main(arglist: List[str] = None, parent_parser: ArgumentParser = None) -> None:
    """Download CLI function for Environment Canada

    Side effect: Sends downloaded XML files to STDOUT.

    :param arglist: Argument list (for testing; default is to parse from sys.argv).
    :param parent_parser: Argument parser common to all network downloads.
    """
    desc = globals()["__doc__"]

    parser = ArgumentParser(parents=[parent_parser], description=desc)
    parser.add_argument("-p", "--province", help="2 letter province code")
    parser.add_argument(
        "-g",
        "--language",
        default="e",
        choices=["e", "f"],
        help="'e' (english) | 'f' (french)",
    )
    parser.add_argument(
        "-F",
        "--frequency",
        choices=["daily", "hourly"],
        help="daily|hourly",
    )
    parser.add_argument(
        "-t",
        "--time",
        help=(
            "Alternate *UTC* time to use for downloading "
            "(interpreted using dateutil.parser.parse)."
            "Defaults to the previous hour/day (depending on"
            " --frequency)."
        ),
    )
    parser.add_argument(
        "-T",
        "--threshold",
        default=1000,
        help=(
            "Distance threshold (in meters) to use when "
            "matching stations. Stations are considered a "
            "match if they have the same id, name, and are "
            "within this threshold"
        ),
    )
    parser.add_argument(
        "-b",
        "--baseurl",
        default="https://hpfx.collab.science.gc.ca",
        help=(
            "Base URL (scheme and hostname components) for"
            "the meteorological observations service"
        ),
    )
    args = parser.parse_args(arglist)

    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd.networks.ec",
    )

    download(args.time, args.frequency, args.province, args.language, args.baseurl)


if __name__ == "__main__":
    main()
