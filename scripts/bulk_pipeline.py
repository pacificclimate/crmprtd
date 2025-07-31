#!/usr/bin/env python

# Standard modules
import os
import sys
import logging
import pytz
from datetime import datetime, timedelta
from argparse import ArgumentParser
from importlib.resources import files
from time import sleep

# Import from crmprtd
from crmprtd import add_logging_args, setup_logging, NETWORKS
from crmprtd.download_cache_process import (
    dispatch,
    network_aliases,
    network_alias_names,
    describe_network,
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
                    cache_filename = generate_cache_filename(
                        opts.cache_directory,
                        opts.network,
                        current_time,
                        opts.frequency,
                        opts.tag,
                    )

                # Call dispatch directly with arguments
                if opts.network == "ec" and opts.province:
                    dispatch(
                        network=opts.network,
                        connection_string=opts.connection_string,
                        dry_run=opts.dry_run,
                        frequency=opts.frequency,
                        tag=opts.tag,
                        time=current_time,
                        cache_filename=cache_filename,
                        province=opts.province,
                    )
                else:
                    dispatch(
                        network=opts.network,
                        connection_string=opts.connection_string,
                        dry_run=opts.dry_run,
                        frequency=opts.frequency,
                        tag=opts.tag,
                        time=current_time,
                        cache_filename=cache_filename,
                    )
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


def generate_cache_filename(cache_dir, network, timestamp, frequency=None, tag=None):
    """Generate cache filename based on parameters"""
    os.makedirs(cache_dir, exist_ok=True)

    ts = timestamp.strftime("%Y-%m-%dT%H:%M:%S")
    tag_prefix = f"{tag}_" if tag else ""
    freq_suffix = f"_{frequency}" if frequency else ""

    if network in ("ec",):
        extension = ".xml"
    elif network in (
        "bc_env_snow",
        "bc_forestry",
        "bc_riotinto",
        "bc_tran",
        "dfo_ccg_lighthouse",
        "nt_forestry",
        "nt_water",
        "yt_gov",
        "yt_water",
        "yt_avalanche",
        "yt_firewx",
    ):
        extension = ".xml"
    else:
        extension = ".txt"

    filename = f"{tag_prefix}{network}_{ts}{freq_suffix}{extension}"
    return os.path.join(cache_dir, filename)


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
        "--cache-directory",
        dest="cache_directory",
        help="Directory to store cache files (if not specified, uses download_cache_process defaults)",
    )
    parser.add_argument(
        "-c",
        "--connection_string",
        dest="connection_string",
        help="Database connection string for processing step",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Print commands without executing them",
    )
    parser.add_argument(
        "--tag",
        dest="tag",
        help="Tag to include in cache and log filenames",
    )

    # EC-specific options
    parser.add_argument(
        "-p",
        "--province",
        dest="province",
        action="append",
        help="Province code(s) for EC network (can be used multiple times)",
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

    # Set defaults
    try:
        with (files("crmprtd") / "data/logging.yaml").open("r") as f:
            default_log_conf = f.name
    except:
        default_log_conf = None

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

    # Handle list networks option
    if opts.list_networks:
        print("Available networks:")
        for network in sorted(NETWORKS):
            print(f"  {network}")
        print("\nAvailable network aliases:")
        for alias in sorted(network_alias_names):
            networks = network_aliases[alias]
            print(f"  {alias}: {', '.join(networks)}")
        sys.exit(0)

    # Validate arguments
    if not opts.network and not opts.list_networks:
        parser.error("Network (-N/--network) is required")

    print(f"Parsed opts: {opts}")
    main(opts, args)
