#!/usr/bin/env python

'''Script to download data from the BC Ministry of Environment Air Quality Branch

Water and Air Monitoring and Reporting? (WAMR)

This is largely lifted and modified from the hourly_wmb.py script
'''

# Standard library module
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
from crmprtd.wamr import setup_logging, rows2db
from crmprtd.wamr import file2rows, ftp2rows
from crmprtd.wamr_dir.download import wamr_download

def main():
    # Process the command line arguments
    parser = ArgumentParser()
    # Database options
    parser.add_argument('-x', '--connection_string',
                        help='PostgreSQL connection string')
    parser.add_argument('-D', '--diag',
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")

    # Logging options
    parser.add_argument('-L', '--log_conf',
                        default=resource_stream(
                            'crmprtd', '/data/logging.yaml'),
                        help='YAML file to use to override the default logging configuration')
    parser.add_argument('-l', '--log',
                        default=None,
                        help='Override the default log filename')
    parser.add_argument('-m', '--error_email',
                        default=None,
                        help='Override the default e-mail address to which the program should report critical errors')
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.  Note that debug output by default goes directly to file')

    # FTP options
    parser.add_argument('-f', '--ftp_server',
                        default='ftp.env.gov.bc.ca',
                        help='Full hostname of Water and Air Monitoring and Reporting\'s ftp server')
    parser.add_argument('-F', '--ftp_dir',
                        default='pub/outgoing/AIR/Hourly_Raw_Air_Data/Meteorological/',
                        help='FTP Directory containing WAMR\'s data files')

    # File input option(s)
    parser.add_argument('-i', '--input_file',
                        default=None,
                        help='')

    # File output options
    parser.add_argument('-c', '--cache_file',
                        default=None,
                        help='Full path of file in which to put downloaded observations (--cache_dir will be ignored)')
    parser.add_argument('-C', '--cache_dir',
                        default='./',
                        help='Directory in which to put downloaded observations (filename will be autogenerated)')
    parser.add_argument('-e', '--error_file',
                        default=None,
                        help='Full path of file in which to put data that could not be added to the database (--error_dir will be ignored)')
    parser.add_argument('-E', '--error_dir',
                        default='./',
                        help='Directory in which to put data that could not be added to the database (filename will be autogenerated)')

    args = parser.parse_args()

    wamr_download(args)

if __name__ == '__main__':
    main()
