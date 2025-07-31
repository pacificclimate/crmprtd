#!/usr/bin/env python

# Standard modules
import os
import glob
import logging
from argparse import ArgumentParser
from importlib.resources import files
import sys

# Import the process function directly instead of main
from crmprtd.process import main as process
from crmprtd import add_logging_args, setup_logging
from scripts import add_bulk_args


def main(opts, args):
    """
    Main function to process multiple files in a directory using crmprtd.process with
    optional pattern matching
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

    # Generate file list based on arguments
    files_to_process = []

    if opts.directory and opts.file_pattern:
        # Process files matching pattern in directory
        pattern_path = os.path.join(opts.directory, opts.file_pattern)
        files_to_process = glob.glob(pattern_path)
        log.info(
            f"Found {len(files_to_process)} files matching pattern '{opts.file_pattern}' in directory '{opts.directory}'"
        )

    elif opts.directory:
        # Process all XML files in directory (default pattern)
        default_pattern = "*.xml"
        pattern_path = os.path.join(opts.directory, default_pattern)
        files_to_process = glob.glob(pattern_path)
        log.info(
            f"Found {len(files_to_process)} XML files in directory '{opts.directory}'"
        )

    elif opts.filename:
        # Process single file
        files_to_process = [opts.filename]
        log.info(f"Processing single file: {opts.filename}")

    elif opts.file_list:
        # Process files from a list file
        with open(opts.file_list, "r") as f:
            files_to_process = [line.strip() for line in f if line.strip()]
        log.info(
            f"Processing {len(files_to_process)} files from list: {opts.file_list}"
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
    if opts.move_processed and valid_files:
        processed_dir = os.path.join(os.path.dirname(valid_files[0]), "processed")
        os.makedirs(processed_dir, exist_ok=True)
        log.info(f"Created processed directory: {processed_dir}")

    base_args = args.copy()

    for i, file_path in enumerate(valid_files, 1):
        log.info(
            f"Processing file {i}/{len(valid_files)}: {os.path.basename(file_path)}"
        )

        try:

            # Open file as binary stream
            with open(file_path, "r") as f:
                # Call process, give back args we've taken from the command line
                # which are consumed by the parser
                f_name = f.name  # Get the file name for logging
            fun_args = [
                *base_args,
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
                "--file",
                f_name,
            ]
            process(fun_args)

            successful_files.append(file_path)
            log.info(f"Successfully processed: {os.path.basename(file_path)}")

            # Move processed file immediately if requested
            if opts.move_processed and processed_dir:
                filename = os.path.basename(file_path)
                new_path = os.path.join(processed_dir, filename)
                os.rename(file_path, new_path)
                log.info(f"Moved processed file: {file_path} -> {new_path}")

        except Exception as e:
            log.error(f"Failed to process file {os.path.basename(file_path)}: {str(e)}")
            failed_files.append((file_path, str(e)))

            if not opts.force:
                log.error("Stopping processing due to error (use -f to continue)")
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
    sysargs = sys.argv[1:]
    parser = ArgumentParser(
        description="Bulk process files using crmprtd.process, for arguments that can be passed to crmprtd.process call crmprtd_process --help"
    )
    add_logging_args(parser)
    add_bulk_args(parser)

    parser.add_argument(
        "-p",
        "--file-pattern",
        default="*.xml",
        help="File pattern to match in directory (default: *.xml)",
    )
    # Processing options
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Continue processing remaining files if one fails",
    )
    parser.add_argument(
        "-M",
        "--move-processed",
        action="store_true",
        help="Move successfully processed files to a 'processed' subdirectory",
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
        error_email="pcic.devops@uvic.ca",
        force=False,
        move_processed=True,
    )

    opts, args = parser.parse_known_args(sysargs)
    main(opts, args)
