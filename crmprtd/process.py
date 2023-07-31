import os
import sys
import pytz
from importlib import import_module
from itertools import tee
import logging
from argparse import ArgumentParser
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pycds import Obs, Network, Variable
import functools
from crmprtd.constants import InsertStrategy
from crmprtd.align import align, cached_function
from crmprtd.insert import insert
from crmprtd.download_utils import verify_date
from crmprtd.infer import infer
from crmprtd import add_version_arg, add_logging_args, setup_logging, NETWORKS
from crmprtd.more_itertools import tap, log_progress

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
    parser.add_argument(
        "-R",
        "--insert_strategy",
        choices=[s.name for s in InsertStrategy],
        default="BULK",
        help=(
            "Strategy to use for inserting observations. The default BULK strategy "
            "handles duplicate observation conflicts inside the database; it is "
            "fastest and is the recommended strategy. The other strategies handle "
            "duplicate observation conflicts outside the database (that is, in this "
            "client), and are considerably slower. They are preserved mainly for "
            "experimentation and comparison. The SINGLE strategy tries inserting the "
            "observations one at a time. The CHUNK_BISECT strategy tries inserting the "
            "observations in fairly large sized chunks, and seeks small sized "
            "sub-chunks if any given chunk fails (because it contains a duplicate). "
            "The ADAPTIVE strategy chooses between SINGLE or CHUNK_BISECT based on a "
            "small randomly selected sample of the observations to be inserted; if all "
            "the observations in this sample are duplicates, it uses SINGLE; "
            "if not, it uses CHUNK_BISECT."
        ),
    )
    parser.add_argument(
        "-C",
        "--bulk_chunk_size",
        type=int,
        default=1000,
        help=(
            "Fixed-length chunk size to use for BULK insertion strategy. Larger "
            "groups of observations to insert are broken into groups of no greater "
            "than this size to prevent possible problems with excessively large "
            "queries."
        ),
    )
    return parser


def get_normalization_module(network):
    return import_module(f"crmprtd.networks.{network}.normalize")


@functools.lru_cache(maxsize=None)
def get_network(sesh, var_id):
    Obs_var = sesh.query(Variable).filter_by(id=var_id).first()
    return Obs_var.network.name


def obs_by_network(observations, sesh):
    obs_by_network_dict = {}
    for obs in observations:
        network_name = get_network(sesh, obs.vars_id)
        if network_name not in obs_by_network_dict:
            obs_by_network_dict[network_name] = []
        obs_by_network_dict[network_name].append(obs)
    return obs_by_network_dict


def process(
    connection_string,
    sample_size,
    network,
    start_date,
    end_date,
    is_diagnostic=False,
    do_infer=False,
    insert_strategy=InsertStrategy.BULK,
    bulk_chunk_size=1000,
    input_stream=None,  # *binary stream* if using a file use open(filname, "rb")
):
    """
    Executes stages of the data processing pipeline.

    1. Get data and normalize it according to which network it is coming from.
    2. Optionally, infer the variables, stations, and histories required by the data.
    3. "Align" the input observations, and remove those not in the specified time range.
    4. Insert the resulting observations.
    """
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

    # Get the normalizer for the specified network.
    norm_mod = get_normalization_module(network)

    if input_stream is None:
        input_stream = sys.stdin.buffer

    log.info("Normalize: start")
    # The normalizer returns a generator that yields `Row`s. Convert to a set of `Row`s.
    # It is probably better to use a dict for this to preserve order.
    # See https://stackoverflow.com/a/9792680
    # Note: Deduplication is important. In some datasets, there is a lot of repetition
    # (factor of 6 in the case of BCH).
    raw_rows = tuple(norm_mod.normalize(input_stream))
    log.info(f"Normalized {len(raw_rows)} rows")
    rows = set(raw_rows)
    log.info(f"Unique normalized rows: {len(rows)}")
    log.info("Normalize: done")

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

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
            tap(
                log_progress(
                    (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 5000),
                    "align progress: {count}",
                    log.info,
                ),
                (
                    align(sesh, row, is_diagnostic)
                    for row in rows
                    if start_date <= row.time <= end_date
                ),
            ),
        )
    )
    log.info("Align + filter: done")

    log.info(f"Count of observations to process: {len(observations)}")
    if is_diagnostic:
        for obs in observations:
            log.info(obs)
        return

    obs_by_network_dict = obs_by_network(observations, sesh)

    log.info("Insert: start")

    for network_key in obs_by_network_dict:
        results = insert(
            sesh,
            obs_by_network_dict[network_key],
            strategy=insert_strategy,
            bulk_chunk_size=bulk_chunk_size,
            sample_size=sample_size,
        )
        log.info("Insert: done")
        log.info(
            "Data insertion results", extra={"results": results, "network": network_key}
        )


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

        args.start_date = utc.localize(
            verify_date(args.start_date, datetime.min, "start date")
        )
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
            insert_strategy=InsertStrategy[args.insert_strategy],
            bulk_chunk_size=args.bulk_chunk_size,
        )
    except Exception:
        log.exception("Unhandled exception during 'process'")


if __name__ == "__main__":
    main()
