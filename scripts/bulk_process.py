#!/usr/bin/env python

# Standard modules
import os
import glob
import logging
from argparse import ArgumentParser
from importlib.resources import files
from datetime import datetime
import pytz

# Import the process function directly instead of main
from crmprtd.process import process
from crmprtd.constants import InsertStrategy
from crmprtd.download_utils import verify_date
from crmprtd import setup_logging


def main(args):
    """
    Main function to process multiple files in a directory using crmprtd.process.

    This script can operate in different modes:
    1. Process all files matching a pattern in a directory
    2. Process a specific file
    3. Process files from a list
    """
    # Create log directory if it doesn't exist
    if args.log_filename:
        log_dir = os.path.dirname(args.log_filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    # Setup logging first
    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd",
    )

    log = logging.getLogger("crmprtd")

    # Parse date arguments - provide defaults if not specified
    utc = pytz.utc
    start_date = utc.localize(verify_date(args.start_date, datetime.min, "start date"))
    end_date = utc.localize(verify_date(args.end_date, datetime.max, "end date"))

    log.info(f"Processing files with date range: {start_date} to {end_date}")

    # Generate file list based on arguments
    files_to_process = []

    if args.directory and args.file_pattern:
        # Process files matching pattern in directory
        pattern_path = os.path.join(args.directory, args.file_pattern)
        files_to_process = glob.glob(pattern_path)
        log.info(
            f"Found {len(files_to_process)} files matching pattern '{args.file_pattern}' in directory '{args.directory}'"
        )

    elif args.directory:
        # Process all XML files in directory (default pattern)
        default_pattern = "*.xml"
        pattern_path = os.path.join(args.directory, default_pattern)
        files_to_process = glob.glob(pattern_path)
        log.info(
            f"Found {len(files_to_process)} XML files in directory '{args.directory}'"
        )

    elif args.filename:
        # Process single file
        files_to_process = [args.filename]
        log.info(f"Processing single file: {args.filename}")

    elif args.file_list:
        # Process files from a list file
        with open(args.file_list, "r") as f:
            files_to_process = [line.strip() for line in f if line.strip()]
        log.info(
            f"Processing {len(files_to_process)} files from list: {args.file_list}"
        )

    else:
        raise ValueError("Must specify either --directory, --filename, or --file-list")

    # Validate files exist
    valid_files = []
    for file_path in files_to_process:
        if os.path.exists(file_path):
            valid_files.append(file_path)
        else:
            log.warning(f"File does not exist, skipping: {file_path}")

    if not valid_files:
        log.error("No valid files found to process")
        return

    log.info(f"Processing {len(valid_files)} files")

    # Process each file
    successful_files = []
    failed_files = []

    # Setup processed directory if needed
    processed_dir = None
    if args.move_processed and valid_files:
        processed_dir = os.path.join(os.path.dirname(valid_files[0]), "processed")
        os.makedirs(processed_dir, exist_ok=True)
        log.info(f"Created processed directory: {processed_dir}")

    for i, file_path in enumerate(valid_files, 1):
        log.info(
            f"Processing file {i}/{len(valid_files)}: {os.path.basename(file_path)}"
        )

        try:
            # Open file as binary stream
            with open(file_path, "rb") as f:
                # Call process function directly with file stream
                process(
                    connection_string=args.connection_string,
                    sample_size=args.sample_size,
                    network=args.network,
                    start_date=start_date,
                    end_date=end_date,
                    is_diagnostic=args.diag,
                    do_infer=args.infer,
                    insert_strategy=InsertStrategy[args.insert_strategy],
                    bulk_chunk_size=args.bulk_chunk_size,
                    input_stream=f,
                )

            successful_files.append(file_path)
            log.info(f"Successfully processed: {os.path.basename(file_path)}")

            # Move processed file immediately if requested
            if args.move_processed and processed_dir:
                filename = os.path.basename(file_path)
                new_path = os.path.join(processed_dir, filename)
                os.rename(file_path, new_path)
                log.info(f"Moved processed file: {file_path} -> {new_path}")

        except Exception as e:
            log.error(f"Failed to process file {os.path.basename(file_path)}: {str(e)}")
            failed_files.append((file_path, str(e)))

            if not args.continue_on_error:
                log.error(
                    "Stopping processing due to error (use --continue-on-error to continue)"
                )
                break

    # Summary
    log.info(
        f"Processing complete. Successfully processed: {len(successful_files)}, Failed: {len(failed_files)}"
    )

    if failed_files:
        log.error("Failed files:")
        for file_path, error in failed_files:
            log.error(f"  {file_path}: {error}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Bulk process files using crmprtd.process")

    # File selection options (mutually exclusive groups would be ideal)
    parser.add_argument(
        "-d", "--directory", help="Directory containing files to process"
    )
    parser.add_argument(
        "-p",
        "--file-pattern",
        default="*.xml",
        help="File pattern to match in directory (default: *.xml)",
    )
    parser.add_argument("-f", "--filename", help="Single file to process")
    parser.add_argument(
        "--file-list",
        help="Text file containing list of files to process (one per line)",
    )

    # Processing options
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing remaining files if one fails",
    )
    parser.add_argument(
        "--move-processed",
        action="store_true",
        help="Move successfully processed files to a 'processed' subdirectory",
    )

    # Arguments passed through to crmprtd.process
    parser.add_argument(
        "-c", "--connection_string", help="PostgreSQL connection string"
    )
    parser.add_argument(
        "-N", "--network", help="The network from which the data is coming from"
    )
    parser.add_argument(
        "-S",
        "--start_date",
        help="Optional start time to use for processing (interpreted with dateutil.parser.parse)",
    )
    parser.add_argument(
        "-E",
        "--end_date",
        help="Optional end time to use for processing (interpreted with dateutil.parser.parse)",
    )
    parser.add_argument(
        "-D", "--diag", action="store_true", help="Turn on diagnostic mode (no commits)"
    )
    parser.add_argument(
        "-I",
        "--infer",
        action="store_true",
        help="Run the 'infer' stage of the pipeline",
    )
    parser.add_argument(
        "-R",
        "--insert_strategy",
        choices=["BULK", "SINGLE", "CHUNK_BISECT", "ADAPTIVE"],
        default="BULK",
        help="Strategy to use for inserting observations",
    )
    parser.add_argument(
        "-C",
        "--bulk_chunk_size",
        type=int,
        default=1000,
        help="Fixed-length chunk size to use for BULK insertion strategy",
    )
    parser.add_argument(
        "--sample_size",
        type=int,
        default=50,
        help="Number of samples to be taken from observations when searching for duplicates",
    )
    parser.add_argument(
        "-y",
        "--log_conf",
        help="YAML file to use to override the default logging configuration",
    )
    parser.add_argument("-l", "--log_filename", help="Log filename")
    parser.add_argument(
        "-e",
        "--error_email",
        help="E-mail address to which the program should report errors",
    )
    parser.add_argument("--log-level", help="Logging level")

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
        error_email="bveerman@uvic.ca",
        continue_on_error=False,
        move_processed=True,
    )

    args = parser.parse_args()
    main(args)
