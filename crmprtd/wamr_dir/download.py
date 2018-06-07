import sys
import csv
import logging
import os

from datetime import datetime
from argparse import ArgumentParser
from pkg_resources import resource_stream

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.wamr import setup_logging
from crmprtd.wamr import file2rows, ftp2rows
from crmprtd.wamr_dir.normalize import prepare


def run(args):
    # Logging
    log = setup_logging(args.log_level, args.log, args.error_email)
    log.info('Starting WAMR rtd')

    # Output files
    if args.error_file:
        error_file = open(args.error_file, 'a')
    else:
        error_filename = 'wamr_errors_{}.csv'.format(datetime.strftime(
                datetime.now(), '%Y-%m-%dT%H-%M-%S'))
        error_file = open(os.path.join(args.cache_dir, error_filename), 'a')

    if args.input_file:
        input_file_prepare(args, error_file, log)
    else:
        # FTP
        rows, fieldnames = ftp2rows(args.ftp_server, args.ftp_dir, log)

        if not args.cache_file:
            args.cache_file = 'wamr_download_{}.csv'.format(datetime.strftime(
                datetime.now(), '%Y-%m-%dT%H-%M-%S'))
        with open(args.cache_file, 'w') as cache_file:
            cache_rows(cache_file, rows, fieldnames)

    log.info('{0} observations read into memory'.format(len(rows)))
    prepare(rows, error_file, log, args)


def cache_rows(file_, rows, fieldnames):
    copier = csv.DictWriter(file_, fieldnames=fieldnames)
    copier.writeheader()
    copier.writerows(rows)
