#!/usr/bin/env python

# From Jim Colley <Jim.Colley@gov.bc.ca>
# "The first file contains a rolling 24hrs of data for each station, and is
# updated at approximately 00:35 past each hour"
#
# FIXME: Replace opts.log with native python logging configuration
# FIMXE: Replace email_error with using a logging handler to catch critical
# errors (i.e. logger.critical()) and do the email

# Standard module
import sys
import csv
import os
import ftplib
import logging

from datetime import datetime
from argparse import ArgumentParser

# Installed libraries
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd import retry, setup_logging, common_script_arguments, \
    common_auth_arguments
from crmprtd.wmb import ObsProcessor, DataLogger


def main(args):
    log = logging.getLogger('crmprtd.wmb')
    log.info('Starting WMB rtd')

    data = []

    # Pull auth from file or command line
    if args.username or args.password:
        auth = {'u': args.username, 'p': args.password}
    else:
        assert args.auth_fname and args.auth_key, ("Must provide both the "
                                                   "auth file and the key to "
                                                   "use for this script "
                                                   "(--auth_key)")
        with open(args.auth_fname, 'r') as f:
            config = yaml.load(f)
        auth = {'u': config[args.auth_key]['username'],
                'p': config[args.auth_key]['password']}

    # Check for local file source
    if args.input_file:
        # adjust to full path
        path = args.input_file
        if args.input_file[0] != '/':
            path = os.path.join(args.archive_dir, args.input_file)
        log.info('Loading local file', extra={'path': path})

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
        log.info('Downloading FTP', extra={'server': args.ftp_server,
                                           'file': args.ftp_file})
        try:
            ftpreader = FTPReader(
                args.ftp_server, auth['u'], auth['p'], args.ftp_file, log)
            log.info('Opened a connection to server',
                     extra={'server': args.ftp_server})
            reader = ftpreader.csv_reader()
            for row in reader:
                data.append(row)
            log.debug('instantiated the reader and processed all rows')
        except ftplib.all_errors as e:
            log.critical('Unable to load data from ftp source', exc_info=True)
            sys.exit(1)

        # save the downloaded file
        fname_out = os.path.join(args.cache_dir,
                                 'wmb_download' +
                                 datetime.strftime(datetime.now(),
                                                   '%Y-%m-%dT%H-%M-%S') +
                                 '.csv')
        with open(fname_out, 'w') as f_out:
            copier = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
            copier.writeheader()
            copier.writerows(data)

    log.info('Observations read into memory', extra={'num_obs': len(data)})
    dl = DataLogger()

    # Open database connection
    try:
        engine = create_engine(args.connection_string)
        Session = sessionmaker(engine)
        sesh = Session()
        sesh.begin_nested()
    except Exception as e:
        dl.add_row(data, 'db-connection error')
        data_archive = dl.archive(args.archive_dir)
        log.critical('Error with database connection, see logfile, data saved',
                     extra={'log': args.log_filename,
                            'data_archive': data_archive})
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
        log.critical('Error with database connection, see logfile, data saved',
                     extra={'log': args.log_filename,
                            'data_archive': data_archive})
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()


class FTPReader(object):
    '''Glue between the FTP_TLS class methods (which are callback based)
       and the csv.DictReader class (which is iteration based)
    '''

    def __init__(self, host, user, password, filename, log=None):
        self.filename = filename

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            return ftplib.FTP_TLS(host, user, password)

        self.connection = ftp_connect_with_retry(host, user, password)

    def csv_reader(self):
        # Just store the lines in memory
        # It's non-ideal but neither classes support coroutine send/yield
        lines = []

        def callback(line):
            lines.append(line)

        self.connection.retrlines('RETR {}'.format(self.filename), callback)

        r = csv.DictReader(lines)
        return r

    def __del__(self):
        try:
            self.connection.quit()
        except Exception:
            self.connection.close()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--ftp_server',
                        default='BCFireweatherFTPp1.nrs.gov.bc.ca',
                        help=('Full uri to Wildfire Management Branch\'s ftp '
                              'server'))
    parser.add_argument('-F', '--ftp_file',
                        default='HourlyWeatherAllFields_WA.txt',
                        help=('Filename to open on the Wildfire Management '
                              'Branch\'s ftp site'))
    parser.add_argument('-a', '--archive_dir',
                        help=('Directory in which to put data that could not '
                              'be added to the database'))
    parser = common_script_arguments(parser)
    parser = common_auth_arguments(parser)
    args = parser.parse_args()
    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.wmb')
    main(args)
