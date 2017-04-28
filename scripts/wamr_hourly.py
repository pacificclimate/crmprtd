#!/usr/bin/env python

'''Script to download data from the BC Ministry of Environment Air Quality Branch

Water and Air Monitoring and Reporting? (WAMR)

This is largely lifted and modified from the hourly_wmb.py script
'''

# Standard library module
import sys
import csv
import logging, logging.config
import os
import socket
import ftplib

from datetime import datetime, timedelta
from argparse import ArgumentParser
from contextlib import closing
from traceback import format_exc
from pkg_resources import resource_stream

# Installed libraries
import requests
from psycopg2 import InterfaceError, ProgrammingError, OperationalError
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd import retry
from crmprtd.wamr import ObsProcessor, DataLogger

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
    log = logging.getLogger('crmprtd.wmb')
    if level:
        log.setLevel(level)

    return log


def main(args):

    log = setup_logging(args.log_level, args.log, args.error_email)
    log.info('Starting WAMR rtd')
    data = []
    
    # Check for local file source
    if args.archive_file:        
        # adjust to full path
        path = args.archive_file
        if args.archive_file[0] != '/':
            path = os.path.join(args.archive_dir, args.archive_file)            
        log.info('Loading local file {0}'.format(path))

        # open and read into data
        try:
            with open(path) as f:
                log.debug('opened the local file')
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except IOError as e:
            log.exception('Unable to load data from local file')
            sys.exit(1)

    # Or use FTP source
    else:
        # Fetch file from FTP and read into memory
        log.info('Fetching file from FTP')

        log.info('Downloading {}/{}'.format(args.ftp_server, args.ftp_file))
        try:
            ftpreader = FTPReader(args.ftp_server, None, None, args.ftp_file, log)
            log.info('Opened a connection to {}'.format(args.ftp_server))
            reader = ftpreader.csv_reader()
            for row in reader:
                data.append(row)
            log.info('instantiated the reader and processed all rows')
        except ftplib.all_errors as e:
            log.critical('Unable to load data from ftp source', exc_info=True)
            sys.exit(1)

        # save the downloaded file
        fname_out = os.path.join(args.cache_dir, 'wmb_download' + datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S') + '.csv')
        with open(fname_out, 'wb') as f_out:
            copier = csv.DictWriter(f_out, fieldnames = reader.fieldnames)
            copier.writeheader()
            copier.writerows(data)

    log.info('{0} observations read into memory'.format(len(data)))
    dl = DataLogger()
    
    # Open database connection
    try:
        engine = create_engine(args.connection_string)
        Session = sessionmaker(engine)
        sesh = Session()
        sesh.begin_nested()
    except Exception as e:
        dl.add_row(data, 'db-connection error')
        log.critical('''Error with Database connection 
                            See logfile at {l}
                            Data saved at {d}
                            '''.format(l = args.log, d = data_archive), exc_info=True)
        sys.exit(1)

    try:
        op = ObsProcessor(sesh, data, args)
        op.process()
        if args.diag:
            log.info('Diagnostic mode, rolling back all transactions')
            sesh.rollback()
        else:
            log.info('Commiting the session')
            sesh.commit()
            
    except Exception as e:
        dl.add_row(data, 'preproc error')
        sesh.rollback()
        data_archive = dl.archive(args.archive_dir)
        log.critical('''Error data preprocessing. 
                            See logfile at {l}
                            Data saved at {d}
                            '''.format(l = args.log, d = data_archive), exc_info=True)
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()


class FTPReader(object):
    '''Glue between the FTP class methods (which are callback based)
       and the csv.DictReader class (which is iteration based)
    '''
    def __init__(self, host, user, password, data_path, log=None):
        self.filenames =[]

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            con = ftplib.FTP(host)
            con.login(user, password)
            return con

        self.connection = ftp_connect_with_retry(host, user, password)
        def callback(line):
            print(line)
            self.filenames.append(line)
        self.connection.retrlines('NLST ' + data_path, callback)
        print(self.filenames)

    def csv_reader(self):
        # Just store the lines in memory
        # It's non-ideal but neither classes support coroutine send/yield
        lines = []
        def callback(line):
            lines.append(line)

        for filename in self.filenames:
            print(filename)
            self.connection.retrlines('RETR {}'.format(filename), callback)

        r = csv.DictReader(lines)
        return r

    def __del__(self):
        try:
            self.connection.quit()
        except:
            self.connection.close()
    
if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string')
    parser.add_argument('-L', '--log_conf',
                        default = resource_stream('crmprtd', '/data/logging.yaml'),
                        help='YAML file to use to override the default logging configuration')
    parser.add_argument('-l', '--log',
                        default = None,
                        help='Override the default log filename')
    parser.add_argument('-e', '--error_email',
                        default = None,
                        help='Override the default e-mail address to which the program should report critical errors')
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.  Note that debug output by default goes directly to file')
    parser.add_argument('-f', '--ftp_server',
                        default = 'ftp.env.gov.bc.ca',
                        help='Full hostname of Water and Air Monitoring and Reporting\'s ftp server')
    parser.add_argument('-F', '--ftp_dir',
                        default = 'pub/outgoing/AIR/Hourly_Raw_Air_Data/Meteorological/',
                        help='FTP Directory containing WAMR\'s data files')
    parser.add_argument('-V', '--variables',
                        default='HUMIDITY,PRECIP,PRESSURE,SNOW,TEMP,VAPOUR,WDIR,WSPD',
                        help='Comma separated list of variables to download')
    parser.add_argument('-C', '--cache_dir',
                        help='Directory in which to put the downloaded file')
    parser.add_argument('-a', '--archive_dir',
                        help='Directory in which to put data that could not be added to the database')
    parser.add_argument('-A', '--archive_file',
                        default = None,
                        help='An archive file to parse INSTEAD OF downloading from ftp. Can be a local reference in the archive_dir or absolute file path')
    parser.add_argument('-D', '--diag', 
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")
    args = parser.parse_args()
    main(args)