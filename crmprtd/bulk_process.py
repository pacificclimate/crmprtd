#!/usr/bin/env python

# Standard modules
import os
import glob
import logging
from argparse import ArgumentParser
from importlib.resources import files
from datetime import datetime
import sys

import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Call the process *function* directly (not its main) so each file is a stream
# fed into one long-lived interpreter and database session, rather than a fresh
# subprocess per file.
from crmprtd.process import process, add_insert_args
from crmprtd.constants import InsertStrategy
from crmprtd.download_utils import verify_date
from crmprtd import add_logging_args, setup_logging, add_bulk_args

log = logging.getLogger("crmprtd")


def resolve_files(opts):
    """The list of files to process, from whichever selection option was given."""
    if opts.directory:
        pattern = opts.file_pattern or "*.xml"
        found = glob.glob(os.path.join(opts.directory, pattern))
        log.info(
            f"Found {len(found)} files matching '{pattern}' in '{opts.directory}'"
        )
        return found
    if opts.filename:
        log.info(f"Processing single file: {opts.filename}")
        return [opts.filename]
    if opts.file_list:
        with open(opts.file_list, "r") as f:
            found = [line.strip() for line in f if line.strip()]
        log.info(f"Processing {len(found)} files from list: {opts.file_list}")
        return found
    raise ValueError("Must specify one of --directory, --filename, or --file_list")


def run(opts):
    """Process every selected file through crmprtd.process, sharing one session."""
    if opts.log_filename:
        log_dir = os.path.dirname(opts.log_filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    setup_logging(
        opts.log_conf,
        opts.log_filename,
        opts.error_email,
        opts.log_level,
        "crmprtd",
    )

    files_to_process = resolve_files(opts)

    valid_files = []
    for file_path in files_to_process:
        if os.path.exists(file_path):
            valid_files.append(file_path)
        else:
            log.warning(f"File does not exist, skipping: {file_path}")

    if not valid_files:
        log.error("No valid files found to process")
        return 0

    log.info(f"Processing {len(valid_files)} files")

    # Moving processed files is opt-in: when the files live in a cache another
    # tool owns (e.g. swobml-sync's), relocating them would corrupt its state.
    processed_dir = None
    if opts.move_processed:
        processed_dir = os.path.join(os.path.dirname(valid_files[0]), "processed")
        os.makedirs(processed_dir, exist_ok=True)
        log.info(f"Created processed directory: {processed_dir}")

    # An optional explicit time window; unbounded by default so every observation
    # in each file is processed.
    utc = pytz.utc
    start_date = utc.localize(
        verify_date(opts.start_date, datetime.min, "start date")
        if opts.start_date
        else datetime.min
    )
    end_date = utc.localize(
        verify_date(opts.end_date, datetime.max, "end date")
        if opts.end_date
        else datetime.max
    )
    insert_strategy = InsertStrategy[opts.insert_strategy]

    # One session for the whole batch: pay connection setup once, not per file.
    sesh = None
    if opts.connection_string:
        engine = create_engine(opts.connection_string)
        sesh = sessionmaker(engine)()

    successful_files = []
    failed_files = []
    totals = {"successes": 0, "skips": 0, "failures": 0}

    for i, file_path in enumerate(valid_files, 1):
        log.info(
            f"Processing file {i}/{len(valid_files)}: {os.path.basename(file_path)}"
        )
        try:
            with open(file_path, "rb") as f:
                results = process(
                    connection_string=opts.connection_string,
                    sample_size=opts.sample_size,
                    network=opts.network,
                    start_date=start_date,
                    end_date=end_date,
                    is_diagnostic=opts.diag,
                    do_infer=opts.infer,
                    insert_strategy=insert_strategy,
                    bulk_chunk_size=opts.bulk_chunk_size,
                    input_stream=f,
                    sesh=sesh,
                )

            successful_files.append(file_path)
            # process() returns None for diagnostic/no-op paths; only sum real results.
            if results:
                for key in totals:
                    totals[key] += results.get(key, 0)
            log.info(f"Successfully processed: {os.path.basename(file_path)}")

            if processed_dir:
                new_path = os.path.join(processed_dir, os.path.basename(file_path))
                os.rename(file_path, new_path)
                log.info(f"Moved processed file: {file_path} -> {new_path}")

        except Exception as e:
            log.error(f"Failed to process file {os.path.basename(file_path)}: {str(e)}")
            failed_files.append((file_path, str(e)))
            # A shared session may be left mid-transaction by the failure; reset it
            # so the remaining files start clean.
            if sesh is not None:
                sesh.rollback()
            if not opts.force:
                log.error("Stopping processing due to error (use -f to continue)")
                break

    # One structured summary line for the whole batch, aggregating the per-file
    # insertion results alongside the file tallies.
    log.info(
        "Bulk insertion results",
        extra={
            "results": {
                **totals,
                "files": len(valid_files),
                "files_succeeded": len(successful_files),
                "files_failed": len(failed_files),
            },
            "network": opts.network,
        },
    )

    if failed_files:
        log.error("Failed files:")
        for file_path, error in failed_files:
            log.error(f"  {file_path}: {error}")
        return 1
    return 0


def main():
    parser = ArgumentParser(
        description=(
            "Bulk process files using crmprtd.process. For processing/insert "
            "arguments, see crmprtd_process --help."
        )
    )
    add_logging_args(parser)
    add_bulk_args(parser)  # -N/--network (required), -d/--directory
    add_insert_args(parser)  # -c, -D/--diag, --sample_size, -R/--insert_strategy, -C

    # Process-phase options (kept out of add_process_args to avoid re-adding -N).
    parser.add_argument(
        "-S", "--start_date", help="Optional start of the time range to process"
    )
    parser.add_argument(
        "-E", "--end_date", help="Optional end of the time range to process"
    )
    parser.add_argument(
        "-I",
        "--infer",
        action="store_true",
        default=False,
        help="Run the 'infer' stage of the pipeline",
    )

    # File selection: exactly one of directory (with optional pattern), a single
    # filename, or a file listing paths one per line.
    parser.add_argument(
        "-p",
        "--file_pattern",
        default="*.xml",
        help="File pattern to match in --directory (default: *.xml)",
    )
    parser.add_argument("--filename", help="Process a single file")
    parser.add_argument(
        "--file_list",
        help="Process every path listed (one per line) in this file",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Continue processing remaining files if one fails",
    )
    parser.add_argument(
        "-M",
        "--move_processed",
        action="store_true",
        help="Move successfully processed files into a 'processed' subdirectory",
    )

    # Set defaults similar to other scripts
    try:
        with (files("crmprtd") / "data/logging.yaml").open("r") as f:
            default_log_conf = f.name
    except:
        default_log_conf = None

    parser.set_defaults(
        connection_string="dbname=crmprtd user=crmp",
        log_conf=default_log_conf,
        log_filename="/tmp/crmp/bulk_process.log",
        log_level="INFO",
        force=False,
        move_processed=False,
    )

    opts = parser.parse_args()
    return run(opts)


if __name__ == "__main__":
    sys.exit(main())
