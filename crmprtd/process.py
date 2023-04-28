import os
import sys
import pytz
from importlib import import_module
from itertools import tee
import logging
from argparse import ArgumentParser
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from pycds import Obs, Variable, Network

from crmprtd.align import align
from crmprtd.insert import insert
from crmprtd.download_utils import verify_date
from crmprtd.infer import infer
from crmprtd import add_version_arg, add_logging_args, setup_logging, NETWORKS


log = logging.getLogger(__name__)


def add_process_args(parser):  # pragma: no cover
    parser.add_argument(
        "-c", "--connection_string", help="PostgreSQL connection string"
    )
    parser.add_argument(
        "-D",
        "--diag",
        default=False,
        action="store_true",
        help="Turn on diagnostic mode (no commits)",
    )
    parser.add_argument(
        "--sample_size",
        type=int,
        default=50,
        help="Number of samples to be taken from observations "
        "when searching for duplicates "
        "to determine which insertion strategy to use",
    )
    parser.add_argument(
        "-N",
        "--network",
        choices=NETWORKS,
        help="The network from which the data is coming from. "
        "The name will be used for a dynamic import of "
        "the module's normalization function.",
    )
    parser.add_argument(
        "-S",
        "--start_date",
        help="Optional start time to use for processing "
        "(interpreted with dateutil.parser.parse).",
    )
    parser.add_argument(
        "-E",
        "--end_date",
        help="Optional end time to use for processing "
        "(interpreted with dateutil.parser.parse).",
    )
    parser.add_argument(
        "-I",
        "--infer",
        default=False,
        action="store_true",
        help="Run the 'infer' stage of the pipeline, which "
        "determines what metadata insertions could be made based"
        "on the observed data available",
    )
    return parser


def get_normalization_module(network):
    return import_module(f"crmprtd.networks.{network}.normalize")


def process(
    connection_string,
    sample_size,
    network,
    start_date=None,
    end_date=None,
    publication_lags=None,
    is_diagnostic=False,
    do_infer=False,
):
    """
    Executes stages of the data processing pipeline.

    1. Get data and normalize it according to which network it is coming from.
    2. Optionally, infer the variables, stations, and histories required by the data.
    3. "Align" the input observations, and remove those not in the specified time range.
    4. Insert the resulting observations.
    """
    # Default value for publication_lags. Too bad there's no (convenient) frozen dict.
    # These values are, I hope, very conservative.
    # TODO: This should be a config value or script arg. Ick.
    #   Also default unspecified networks to a particular timedelta. Hard to say
    #   what.
    if publication_lags is None:
        publication_lags = {
            # BCH: New values are published weekly in a 3-month rolling window.
            # For the sake of safety, assume that some new values include values
            # for observations dated not just in the past week, but a week before
            # as well. Is this actually possible?
            "bc_hydro": timedelta(days=14)
        }

    if network == "_test":
        log.info(f"PATH={os.environ['PATH']}")
        log.info(f"Network {network}: No-op")
        return

    if network is None:
        log.error(
            "No network name given, cannot continue pipeline",
            extra={"network": network},
        )
        raise ValueError("No network name given")

    # Establish a database session
    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    # For network bc_hydro (at present, # *only* bc_hydro): If start_date is not
    # specified, determine it from latest obs time in database.
    # This typically takes on the order of 90 s, but that cost is not remotely the cost
    # of trying to insert - one by one - observations that are already present.
    if network == "bc_hydro" and start_date is None:
        log.info("Querying database for latest obs time...")
        latest_obs_time = (
            sesh.query(func.max(Obs.time))
            .select_from(Obs)
            .join(Variable)
            .join(Network)
            .filter(Network.name == "BCH")
            .scalar()
        )
        log.info(
            f"For network {network}, latest obs time from query = {latest_obs_time}"
        )
        # Obs.time is implicitly UTC, but we need to add that info to the unlocalized
        # value we get from the database. Also, handle case where the query returns no
        # value.
        latest_obs_time = (
            pytz.utc.localize(latest_obs_time)
            if latest_obs_time is not None
            else datetime.min
        )
        start_date = latest_obs_time - publication_lags[network]

    # For all other cases, replace start_date == None with datetime.min.
    if start_date is None:
        start_date = datetime.min
    # At present, this is impossible, but hey, it's cheap insurance.
    if end_date is None:
        start_date = datetime.max
    log.info(
        f"Final time filter parameters: "
        f"start_date = {start_date}, end_date = {end_date}"
    )

    # Get the normalizer for the specified network.
    download_stream = sys.stdin.buffer
    norm_mod = get_normalization_module(network)

    log.info("Normalize: start")
    # The normalizer returns a generator that yields `Row`s. Convert to a set of Rows.
    # It is probably better to use a dict for this to preserve order.
    # See https://stackoverflow.com/a/9792680
    rows = {row for row in norm_mod.normalize(download_stream)}
    log.debug(f"Found {len(rows)} rows.")
    log.info("Normalize: done")

    # Optionally infer variables and stations/histories.
    if do_infer:
        infer(sesh, rows, is_diagnostic)

    # Filter the observations by time period, then align them.
    log.info("Align + filter: start")
    observations = list(
        # Note: filter(None, <collection>) removes falsy values from <collection>,
        # in this case possible None values returned by align.
        filter(
            None,
            (
                align(sesh, row, is_diagnostic)
                for row in rows
                if start_date <= row.time <= end_date
            ),
        )
    )
    log.info("Align + filter: done")

    log.info(f"Count of observations to process: {len(observations)}")
    if is_diagnostic:
        for obs in observations:
            log.info(obs)
        return

    log.info("Insert: start")
    results = insert(sesh, observations, sample_size)
    log.info("Insert: done")
    log.info("Data insertion results", extra={"results": results, "network": network})


# Note: this function was buried in crmprtd.__init__.py but is
# currently (c.a. 2020-12-04) unused. It *may* have some utility at
# some point, particularly if refactored with process(), so it is
# reproduced here.
def run_data_pipeline(
    download_func,
    normalize_func,
    download_args,
    cache_file,
    connection_string,
    sample_size,
):  # pragma: no cover
    """Executes all stages of the data processing pipeline.

    Downloads the data, according to the download arguments
    provided (generally from the command line), normalizes the data
    based on the network's format. The the fuction send the
    normalized rows through the align and insert phases of the
    pipeline.
    """
    download_iter = download_func(**download_args)

    if cache_file:
        download_iter, cache_iter = tee(download_iter)
        with open(cache_file, "w") as f:
            for chunk in cache_iter:
                f.write(chunk)

    rows = list(normalize_func(download_iter))

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    observations = [ob for ob in [align(sesh, row) for row in rows] if ob]
    results = insert(sesh, observations, sample_size)

    log = logging.getLogger(__name__)
    log.info("Data insertion results", extra={"results": results})


def main(args=None):
    try:
        parser = ArgumentParser()
        add_version_arg(parser)
        add_process_args(parser)
        add_logging_args(parser)
        args = parser.parse_args(args)

        setup_logging(
            args.log_conf,
            args.log_filename,
            args.error_email,
            args.log_level,
            "crmprtd",
        )

        utc = pytz.utc

        # Value of None for start_date is meaningful: it means, for some networks,
        # determine from database. Pass that through.
        args.start_date = args.start_date and utc.localize(
            verify_date(args.start_date, datetime.max, "start date")
        )
        # Not so for end_date.
        args.end_date = utc.localize(
            verify_date(args.end_date, datetime.max, "end date")
        )

        process(
            connection_string=args.connection_string,
            sample_size=args.sample_size,
            network=args.network,
            start_date=args.start_date,
            end_date=args.end_date,
            is_diagnostic=args.diag,
            do_infer=args.infer,
        )
    except Exception:
        log.exception("Unhandled exception during 'process'")


if __name__ == "__main__":
    main()
