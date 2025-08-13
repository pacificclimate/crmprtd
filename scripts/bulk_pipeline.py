#!/usr/bin/env python

# Standard modules
import os
import sys
import logging
import pytz
from datetime import datetime, timedelta
from argparse import ArgumentParser
from time import sleep
from importlib.resources import files

# Import from crmprtd
from crmprtd import add_logging_args, setup_logging, NETWORKS
from crmprtd.download_cache_process import (
    main as download_cache_process_main,
    describe_network,
    default_cache_filename,
)
from scripts import add_bulk_args, add_time_range_args


def main(opts, args):
    """
    Main function to run bulk pipeline operations using download_cache_process
    for time ranges with specified frequency
    """
    # Create log directory if it doesn't exist
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

    log = logging.getLogger("crmprtd")

    log.info(f"Network description: {describe_network(opts.network)}")

    try:
        stime = datetime.strptime(opts.stime, "%Y-%m-%d %H:%M:%S")
        etime = datetime.strptime(opts.etime, "%Y-%m-%d %H:%M:%S")

        # Truncate timestamps to nearest hour
        stime = stime.replace(minute=0, second=0, microsecond=0)
        etime = etime.replace(minute=0, second=0, microsecond=0)

        if opts.frequency == "hourly":
            timestep = timedelta(hours=1)
        elif opts.frequency == "daily":
            timestep = timedelta(days=1)
        else:
            raise ValueError("Frequency must be 'hourly' or 'daily'")

        log.info(
            f"Running pipeline from {stime} to {etime} with {opts.frequency} frequency"
        )

        successful_runs = 0
        failed_runs = 0

        current_time = stime
        while current_time <= etime:
            iter_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            log.info(f"Processing time: {iter_time_str}")

            try:
                # Generate cache filename if directory specified
                cache_filename = None
                if opts.cache_directory:
                    
                    cache_filename = default_cache_filename(
                        timestamp=current_time,
                        network_name=opts.network,
                        tag=opts.tag,
                        frequency=opts.frequency if opts.network == "ec" else None,
                        province=opts.province if opts.network == "ec" else None,
                    )

                    # Replace the default cache directory with the user-specified directory
                    cache_filename = cache_filename.replace(
                        f"~/{opts.network}/cache/", f"{opts.directory}/"
                    )

                # Build argument list for download_cache_process main function
                # Start with base arguments from the original args list
                base_args = args.copy()

                # Construct the full argument list with all required parameters
                fun_args = [
                    *base_args,
                    "--network",
                    opts.network,
                    # "--log_conf",
                    # opts.log_conf,
                    "--log_filename",
                    opts.log_filename,
                    # "--log_level",
                    # opts.log_level,
                    # "--error_email",
                    # opts.error_email,
                ]

                # Add frequency if provided (only for EC network, as other networks don't use it)
                if opts.network == "ec" and opts.frequency:
                    fun_args.extend(["--frequency", opts.frequency])

                # Add tag if provided
                if opts.tag:
                    fun_args.extend(["--tag", opts.tag])

                # Add cache filename if specified
                if opts.cache_directory:
                    fun_args.extend(["--cache_filename", cache_filename])

                # Add time parameter (now supported by download_cache_process.main())
                fun_args.extend(["--time", current_time.strftime("%Y-%m-%d %H:%M:%S")])

                # Call download_cache_process main function with constructed arguments
                download_cache_process_main(fun_args)
                successful_runs += 1
                log.info(f"Successfully processed: {iter_time_str}")

            except Exception as e:
                failed_runs += 1
                log.error(f"Failed to process time {iter_time_str}: {str(e)}")
                if not opts.force:
                    log.error("Stopping due to error (use --force to continue)")
                    break

            current_time += timestep

            if opts.delay > 0:
                sleep(opts.delay)

        log.info(
            f"Time range processing complete. Success: {successful_runs}, Failed: {failed_runs}"
        )

    except Exception as e:
        log.error(f"Error in time range processing: {str(e)}")
        raise


if __name__ == "__main__":
    sysargs = sys.argv[1:]
    parser = ArgumentParser(
        description="Bulk pipeline operations using download_cache_process functions for time ranges"
    )

    add_logging_args(parser)
    add_bulk_args(parser)
    add_time_range_args(parser, start_required=True, frequency_required=True)

    # Cache and processing options
    parser.add_argument(
        "--cache_directory",
        dest="cache_directory",
        help="Directory to store cache files (if not specified, uses download_cache_process defaults)",
    )
    parser.add_argument(
        "--tag",
        dest="tag",
        help="Tag to include in cache and log filenames",
    )
    # Control options
    parser.add_argument(
        "--force",
        dest="force",
        action="store_true",
        help="Continue processing if individual operations fail",
    )
    parser.add_argument(
        "--delay",
        dest="delay",
        type=int,
        default=3,
        help="Delay in seconds between operations (default: 3)",
    )

    try:
        with (files("crmprtd") / "data/logging.yaml").open("r") as f:
            default_log_conf = f.name
    except:
        default_log_conf = None

    # Set defaults
    parser.set_defaults(
        log_conf=default_log_conf,
        log_filename="/tmp/crmp/bulk_pipeline.log",
        log_level="INFO",
        error_email="pcic.devops@uvic.ca",
        etime=datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S"),
        dry_run=False,
        force=False,
        delay=3,
    )

    opts, args = parser.parse_known_args(sysargs)

    # Validate arguments
    if not opts.network:
        parser.error("Network (-N/--network) is required")

    logging.info(f"Parsed opts: {opts}")
    main(opts, args)
