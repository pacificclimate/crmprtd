#!/usr/bin/env python

# Standard module
import os
import pytz
import sys
from datetime import datetime, timedelta
from argparse import ArgumentParser
from importlib.resources import files
from time import sleep
from crmprtd import add_logging_args, setup_logging
from scripts import add_bulk_args, add_time_range_args
from crmprtd.download import main as download_main
from crmprtd.download_cache_process import default_cache_filename
from contextlib import redirect_stdout


def main(opts, args):# Create log directory if it doesn't exist
    
    if opts.log_filename:
        log_dir = os.path.dirname(opts.log_filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    # Setup logging first
    setup_logging(
        opts.log_conf,
        opts.log_filename,
        opts.error_email,
        opts.log_level,
        "crmprtd",
    )
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
            raise ValueError("Frequency must be 'hourly' or 'daily'")
            raise ValueError("Frequency must be 'hourly' or 'daily'")

        base_args = args.copy()
        while stime <= etime:
            iter_time = datetime.strftime(stime, "%Y-%m-%d %H:%M:%S")
            # re-inject args we've consumed that might be used by the download function
            # argsparse for the bulk downloader steals these arguments, so we need to pass them back into the list
            fun_args = [
                *base_args,
                "--time",
                iter_time,
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
            # Add frequency if provided (only for EC network, as other networks don't use it)
            if opts.network == "ec" and opts.frequency:
                fun_args.extend(["--frequency", opts.frequency])
            
            # Add tag if provided
            if opts.tag:
                fun_args.extend(["--tag", opts.tag])
            
            # Add province if provided
            if opts.province:
                fun_args.extend(["--province", opts.province])

            # Use default_cache_filename to ensure consistent filename generation
            cache_filename = default_cache_filename(
                timestamp=stime,
                network_name=opts.network,
                frequency=opts.frequency if opts.network == "ec" else None,
                province=opts.province if opts.network == "ec" else None,
                tag=opts.tag
            )
            # Replace the default cache directory with the user-specified directory
            cache_filename = cache_filename.replace(f"~/{opts.network}/cache/", f"{opts.directory}/")
            
            with open(cache_filename, "w") as f:
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
    
    # Add tag argument for filename generation
    parser.add_argument(
        "-T",
        "--tag",
        help="Tag for forming default names for cache files",
    )
    
    parser.add_argument(
        "-p",
        "--province",
        help="Province for forming default names for cache files",
    )

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
