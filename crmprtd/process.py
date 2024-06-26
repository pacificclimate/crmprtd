import os
import sys
import pytz
from importlib import import_module
from itertools import tee, islice
import logging
from argparse import ArgumentParser
from datetime import datetime
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from crmprtd.constants import InsertStrategy
from crmprtd.align import align
from crmprtd.insert import insert
from crmprtd.download_utils import verify_date
from crmprtd.infer import infer
from crmprtd import add_version_arg, add_logging_args, setup_logging, NETWORKS
from crmprtd.more_itertools import tap, log_progress
from pycds import Obs

log = logging.getLogger(__name__)


def add_insert_args(parser):  # pragma: no cover
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


def add_process_args(parser):  # pragma: no cover
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

    log.info("Insert: start")
    results = insert(
        sesh,
        observations,
        strategy=insert_strategy,
        bulk_chunk_size=bulk_chunk_size,
        sample_size=sample_size,
    )
    log.info("Insert: done")
    log.info("Data insertion results", extra={"results": results, "network": network})


def gulpy_plus_plus():
    """A stripped down processing pipeline for users that have already
    preprocessed their data into tuples of ("history_id", "time", "datum",
    "vars_id"), and saved them as a CSV file"""

    parser = ArgumentParser()
    add_version_arg(parser)
    add_insert_args(parser)
    add_logging_args(parser)
    parser.add_argument(
        "-N",
        "--network",
        help="The network from which the data is coming from. "
        "Since gulpy input already identifies the network by way of the provided history_ids, the name will only be used for logging.",
    )
    parser.add_argument('filenames', metavar='filename', nargs='+',
                        help='CSV files to process')
    args = parser.parse_args()

    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd",
    )

    engine = create_engine(args.connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    fieldnames = ("history_id", "time", "datum", "vars_id")
    for fname in args.filenames:
        with open(fname) as csvfile:
            reader = csv.DictReader(csvfile, fieldnames)
            observations = [Obs(**row) for row in islice(reader, 1, None)]

        log.info(f"Count of observations to process: {len(observations)}")
        if args.diag:
            for obs in observations:
                log.info(obs)
            continue

        log.info("Insert: start")
        results = insert(
            sesh,
            observations,
            strategy=InsertStrategy[args.insert_strategy],
            bulk_chunk_size=args.bulk_chunk_size,
            sample_size=args.sample_size,
        )
        log.info("Insert: done")
        log.info(
            "Data insertion results",
            extra={"results": results, "network": args.network},
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
        add_insert_args(parser)
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
