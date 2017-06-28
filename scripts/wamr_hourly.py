#!/usr/bin/env python

'''Script to download data from the BC Ministry of Environment Air Quality Branch

Water and Air Monitoring and Reporting? (WAMR)

This is largely lifted and modified from the hourly_wmb.py script
'''

# Standard library module
import sys
import csv
import logging
import logging.config
import os
import ftplib

from datetime import datetime
from argparse import ArgumentParser
from contextlib import closing
from pkg_resources import resource_stream

# Installed libraries
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd import retry
from crmprtd.db import mass_insert_obs
from crmprtd.wamr import process_obs, DataLogger
from crmprtd.wamr import create_station_mapping, create_variable_mapping


def setup_logging(level, filename=None, email=None):
    '''Read in the logging configuration and return a logger object
    '''
    log_conf = yaml.load(resource_stream('crmprtd', '/data/logging.yaml'))
    if filename:
        log_conf['handlers']['file']['filename'] = filename
    else:
        filename = log_conf['handlers']['file']['filename']
    if email:
        log_conf['handlers']['mail']['toaddrs'] = email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger('crmprtd.wamr')
    if level:
        log.setLevel(level)

    return log


def rows2db(sesh, rows, error_file, log, diagnostic=False):
    '''
    Args:
        sesh (sqlalchemy.Session): The first parameter.
        rows ():
        error_file ():
        log (): The second parameter.

    '''
    dl = DataLogger(log)

    sesh.begin_nested()

    try:
        log.debug('Processing observations')
        histories = create_station_mapping(sesh, rows)
        variables = create_variable_mapping(sesh, rows)

        obs = []
        for row in rows:
            try:
                obs.append(process_obs(sesh, row, log, histories, variables))
            except Exception as e:
                dl.add_row(row, e.args[0]) # FIXME: no args here

        log.info("Starting a mass insertion of %d obs", len(obs))
        n_insertions = mass_insert_obs(sesh, obs, log)
        log.info("Inserted %d obs", n_insertions)

        if diagnostic: 
            log.info('Diagnostic mode, rolling back all transactions')
            sesh.rollback()
        else:
            log.info('Commiting the sesh')
            sesh.commit()

    except Exception as e: # FIXME: sqlalchemy.exc.OperationalError? (cannot connect to db) sqlalchemy.exc.InternalError (read-only transaction)
        dl.add_row(rows, 'preproc error')
        sesh.rollback()
        data_archive = dl.archive(error_file)
        log.critical('''Error data preprocessing. 
                            See logfile at {l}
                            Data saved at {d}
                            '''.format(l=args.log, d=data_archive), exc_info=True) # FIXME: no args here
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()

    dl.archive(error_file)


class FTPReader(object):
    '''Glue between the FTP class methods (which are callback based)
       and the csv.DictReader class (which is iteration based)
    '''

    def __init__(self, host, user, password, data_path, log=None):
        self.filenames = []

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            con = ftplib.FTP(host)
            con.login(user, password)
            return con

        self.connection = ftp_connect_with_retry(host, user, password)

        def callback(line):
            self.filenames.append(line)

        self.connection.retrlines('NLST ' + data_path, callback)

    def csv_reader(self, log=None):
        # Just store the lines in memory
        # It's non-ideal but neither classes support coroutine send/yield
        if not log:
            log = logging.getLogger('__name__')
        lines = []

        def callback(line):
            lines.append(line)

        for filename in self.filenames:
            log.info("Downloading %s", filename)
            # FIXME: This line has some kind of race condition with this
            self.connection.retrlines('RETR {}'.format(filename), callback)

        r = csv.DictReader(lines)
        return r

    def __del__(self):
        try:
            self.connection.quit()
        except:
            self.connection.close()


def file2rows(file_, log):
    try:
        reader = csv.DictReader(file_)
    except csv.Error as e:
        log.critical('Unable to load data from local file', exc_info=True)
        sys.exit(1)

    return [row for row in reader], reader.fieldnames


def ftp2rows(host, path, log):
    log.info('Fetching file from FTP')
    log.info('Listing {}/{}'.format(host, path))

    try:
        ftpreader = FTPReader(host, None,
                              None, path, log)
        log.info('Opened a connection to {}'.format(host))
        reader = ftpreader.csv_reader(log)
        log.info('instantiated the reader and downloaded all of the data')
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)

    return [row for row in reader], reader.fieldnames


def cache_rows(file_, rows, fieldnames):
    copier = csv.DictWriter(file_, fieldnames=fieldnames)
    copier.writeheader()
    copier.writerows(rows)


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

    # Open up any resources that we need for the program

    # Logging
    log = setup_logging(args.log_level, args.log, args.error_email)
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
    else: #FTP
        rows, fieldnames = ftp2rows(args.ftp_server, args.ftp_dir, log)

        if not args.cache_file:
            args.cache_file = 'wamr_download_{}.csv'.format(datetime.strftime(
                datetime.now(), '%Y-%m-%dT%H-%M-%S'))
        with open(args.cache_file, 'w') as cache_file:
            cache_rows(cache_file, rows, fieldnames)

    log.info('{0} observations read into memory'.format(len(rows)))

    # Hand the row off to the database processings/insertion part of the script
    rows2db(sesh, rows, error_file, log)


if __name__ == '__main__':
    main()
