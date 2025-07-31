#!/usr/bin/env python

# Standard module
import pytz
import sys
from datetime import datetime, timedelta
from argparse import ArgumentParser
from importlib.resources import files
from time import sleep
from crmprtd import add_logging_args
from scripts import add_bulk_args, add_time_range_args
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
                "--log_conf",
                opts.log_conf,
                "--log_filename",
                opts.log_filename,
                "--log_level",
                opts.log_level,
                "--error_email",
                opts.error_email,
            ]

            # save this file to the cache directory, with a file name based on the network, timestamp, and frequency
            with open(
                f"{opts.directory}/{opts.network}_{iter_time.replace(':', '-')}_{opts.frequency}.xml",
                "w",
            ) as f:
                with redirect_stdout(f):
                    download_main(fun_args)
            stime += timestep
            sleep(3)  # Avoid overwhelming the server with requests


if __name__ == "__main__":
    sysargs = sys.argv[1:]
    parser = ArgumentParser()

    add_logging_args(parser)
    add_bulk_args(parser)
    add_time_range_args(parser, start_required=False, frequency_required=True)

    # Set defaults similar to other scripts
    try:
        with (files("crmprtd") / "data/logging.yaml").open("r") as f:
            default_log_conf = f.name
    except:
        default_log_conf = None

    parser.set_defaults(
        log_conf=default_log_conf,
        log_filename="/tmp/crmp/download_main.txt",
        log_level="INFO",
        error_email="pcic.devops@uvic.ca",
        directory="~/bulk_download",
        time=None,
        stime=None,
        etime=datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S"),
    )

    opts, args = parser.parse_known_args(sysargs)
    print(f"Parsed opts: {opts}")
    main(opts, args)
