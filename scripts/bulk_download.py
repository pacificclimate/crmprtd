#!/usr/bin/env python

# Standard module
import pytz
import sys
from datetime import datetime, timedelta
from argparse import ArgumentParser
from importlib.resources import files
from time import sleep
from crmprtd.download import main as download_main
from contextlib import redirect_stdout


def main(opts, args):
    if opts.stime and opts.etime:
        # Range mode: start and end times are provided
        # It is assumed that start and end times are correctly formatted on entry
        # Exceptions are not handled by design.
        stime = datetime.strptime(opts.stime, "%Y-%m-%d %H:%M:%S")
        etime = datetime.strptime(opts.etime, "%Y-%m-%d %H:%M:%S")

        # Truncate timestamps to drop minute and second components (round down to nearest hour)
        # as we'd usually be pretty close to the hour mark as part of the cron jobs
        stime = stime.replace(minute=0, second=0, microsecond=0)
        etime = etime.replace(minute=0, second=0, microsecond=0)

        if opts.frequency == "hourly":
            timestep = timedelta(hours=1)
        elif opts.frequency == "daily":
            timestep = timedelta(days=1)
        else:
            raise Exception("Frequency must be 'hourly' or 'daily'")

        base_args = args.copy()
        while stime <= etime:
            iter_time = datetime.strftime(stime, "%Y-%m-%d %H:%M:%S")
            # inject time, frequency, and network into the download function via the args
            # argsparse for the bulk downloader steals these arguments, so we need to pass them back into the list
            fun_args = [
                *base_args,
                "--time",
                iter_time,
                "--frequency",
                opts.frequency,
                "--network",
                opts.network,
            ]

            # save this file to the cache directory, with a file name based on the network, timestamp, and frequency
            with open(
                f"{opts.cache_dir}/{opts.network}_{iter_time.replace(':', '-')}_{opts.frequency}.xml",
                "w",
            ) as f:
                with redirect_stdout(f):
                    download_main(fun_args)
            stime += timestep
            sleep(3)  # Avoid overwhelming the server with requests


if __name__ == "__main__":
    sysargs = sys.argv[1:]
    parser = ArgumentParser(conflict_handler="resolve")
    parser.add_argument(
        "-y",
        "--log_conf",
        dest="log_conf",
        help=("YAML file to use to override the default logging " " configuration"),
    )
    parser.add_argument("-l", "--log", dest="log", help="log filename")
    parser.add_argument(
        "-C",
        "--cache_dir",
        dest="cache_dir",
        help=(
            "directory in which to put the downloaded file in "
            "the event of a post-download error"
        ),
    )
    parser.add_argument(
        "-D",
        "--diag",
        dest="diag",
        action="store_true",
        help="Turn on diagnostic mode (no commits)",
    )
    parser.add_argument(
        "--start",
        dest="stime",
        help=(
            "Start time of range to recover (interpreted with "
            "strptime(format='%%Y-%%m-%%d %%H:%%M:%%S')"
        ),
    )
    parser.add_argument(
        "--end",
        dest="etime",
        help=(
            "End time of range to recover (interpreted with "
            "strptime(format='%%Y-%%m-%%d %%H:%%M:%%S')"
        ),
    )
    parser.add_argument(
        "-N",
        "--network",
        dest="network",
        help="The network from which the data is coming from",
    )
    parser.add_argument(
        "-F",
        "--frequency",
        dest="frequency",
        required=True,
        choices=["daily", "hourly"],
        help="daily|hourly - frequency for bulk download",
    )

    with (files("crmprtd") / "data/logging.yaml").open("rb") as f:
        parser.set_defaults(
            log_conf=f,
            log="/tmp/crmp/download_main.txt",
            error_email="pcic.devops@uvic.ca",
            cache_dir="/home/data/projects/crmprtd/bulk_download",
            diag=False,
            time=None,
            stime=None,
            etime=datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S"),
        )
    opts, args = parser.parse_known_args(sysargs)
    print(f"Parsed opts: {opts}")
    main(opts, args)
