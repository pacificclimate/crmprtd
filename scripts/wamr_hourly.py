#!/usr/bin/env python

'''
Script to download data from the BC Ministry of Environment Air Quality Branch

Water and Air Monitoring and Reporting? (WAMR)

This is largely lifted and modified from the hourly_wmb.py script
'''

# Standard library module
import sys
import csv
import os

from datetime import datetime
from argparse import ArgumentParser
import logging

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd import setup_logging, common_script_arguments
from crmprtd.wamr import rows2db, file2rows, ftp2rows


def cache_rows(file_, rows, fieldnames):
    copier = csv.DictWriter(file_, fieldnames=fieldnames)
    copier.writeheader()
    copier.writerows(rows)


def main():
    parser = ArgumentParser()
    parser.add_argument('-f', '--ftp_server',
                        default='ftp.env.gov.bc.ca',
                        help=('Full hostname of Water and Air Monitoring and '
                              'Reporting\'s ftp server'))
    parser.add_argument('-F', '--ftp_dir',
                        default=('pub/outgoing/AIR/Hourly_Raw_Air_Data/'
                                 'Meteorological/'),
                        help='FTP Directory containing WAMR\'s data files')
    parser.add_argument('-e', '--error_file',
                        default=None,
                        help=('Full path of file in which to put data that '
                              'could not be added to the database'))

    parser = common_script_arguments(parser)
    args = parser.parse_args()

    # Logging
    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.wamr')
    log = logging.getLogger('crmprtd.wamr')
    log.info('Starting WAMR rtd')

    # Database connection
    try:
        engine = create_engine(args.connection_string)
        Session = sessionmaker(engine)
        sesh = Session()
    except Exception as e:
        log.critical('Error with Database connection', exc_info=True)
        sys.exit(1)

    # Output files
    if args.error_file:
        error_file = open(args.error_file, 'a')
    else:
        error_filename = 'wamr_errors_{}.csv'.format(datetime.strftime(
            datetime.now(), '%Y-%m-%dT%H-%M-%S'))
        error_file = open(os.path.join(args.cache_dir, error_filename), 'a')

    if args.input_file:
        with open(args.input_file) as f:
            rows, fieldnames = file2rows(f, log)
    else:  # FTP
        rows, fieldnames = ftp2rows(args.ftp_server, args.ftp_dir, log)

        if not args.cache_file:
            args.cache_file = 'wamr_download_{}.csv'.format(datetime.strftime(
                datetime.now(), '%Y-%m-%dT%H-%M-%S'))
        with open(args.cache_file, 'w') as cache_file:
            cache_rows(cache_file, rows, fieldnames)

    log.info('observations read into memory', extra={'num_obs': len(rows)})

    # Hand the row off to the database processings/insertion part of the script
    rows2db(sesh, rows, error_file, log, args.diag)


if __name__ == '__main__':
    main()
