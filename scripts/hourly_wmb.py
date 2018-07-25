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
import logging
import logging.config
import os
import ftplib
import gzip

from datetime import datetime
from argparse import ArgumentParser
from pkg_resources import resource_stream

# Installed libraries
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd import retry
from crmprtd.wmb import ObsProcessor, DataLogger


def main(args):
    # Setup logging
    log_conf = yaml.load(resource_stream('crmprtd', '/data/logging.yaml'))
    if args.log:
        log_conf['handlers']['file']['filename'] = args.log
    else:
        args.log = log_conf['handlers']['file']['filename']
    if args.error_email:
        log_conf['handlers']['mail']['toaddrs'] = args.error_email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger('crmprtd.wmb')
    if args.log_level:
        log.setLevel(args.log_level)

    data = []

    # Pull auth from file or command line
    if args.username or args.password:
        auth = {'u': args.username, 'p': args.password}
    else:
        assert args.auth and args.auth_key, ("Must provide both the auth file "
                                             "and the key to use for this "
                                             "script (--auth_key)")
        with open(args.auth, 'r') as f:
            config = yaml.load(f)
        auth = {'u': config[args.auth_key]['username'],
                'p': config[args.auth_key]['password']}

    # Check for local file source
    if args.archive_file:
        # adjust to full path
        path = args.archive_file
        if args.archive_file[0] != '/':
            path = os.path.join(args.archive_dir, args.archive_file)
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
        if args.compress:
            with gzip.open(fname_out + '.gz', 'wt') as f_out:
                copier = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
                copier.writeheader()
                copier.writerows(data)
        else:
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
                     extra={'log': args.log, 'data_archive': data_archive})
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
                     extra={'log': args.log, 'data_archive': data_archive})
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
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string')
    parser.add_argument('-L', '--log_conf',
                        default=resource_stream(
                            'crmprtd', '/data/logging.yaml'),
                        help=('YAML file to use to override the default '
                              'logging configuration'))
    parser.add_argument('-l', '--log',
                        default=None,
                        help='Override the default log filename')
    parser.add_argument('-e', '--error_email',
                        default=None,
                        help=('Override the default e-mail address to which '
                              'the program should report critical errors'))
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        help=('Set log level: DEBUG, INFO, WARNING, ERROR, '
                              'CRITICAL.  Note that debug output by default '
                              'goes directly to file'))
    parser.add_argument('-f', '--ftp_server',
                        default='BCFireweatherFTPp1.nrs.gov.bc.ca',
                        help=('Full uri to Wildfire Management Branch\'s ftp '
                              'server'))
    parser.add_argument('-F', '--ftp_file',
                        default='HourlyWeatherAllFields_WA.txt',
                        help=('Filename to open on the Wildfire Management '
                              'Branch\'s ftp site'))
    parser.add_argument('--auth',
                        help="Yaml file with plaintext usernames/passwords")
    parser.add_argument('--auth_key',
                        help=("Top level key which user/pass are stored in "
                              "yaml file."))
    parser.add_argument('--username',
                        help=("The username for data requests. Overrides auth "
                              "file."))
    parser.add_argument('--password',
                        help=("The password for data requests. Overrides auth "
                              "file."))
    parser.add_argument('-C', '--cache_dir',
                        help='Directory in which to put the downloaded file')
    parser.add_argument('-P', '--compress',
                        action='store_true',
                        help='Compress saved download file')
    parser.add_argument('-a', '--archive_dir',
                        help=('Directory in which to put data that could not '
                              'be added to the database'))
    parser.add_argument('-A', '--archive_file',
                        default=None,
                        help=('An archive file to parse INSTEAD OF '
                              'downloading from ftp. Can be a local reference '
                              'in the archive_dir or absolute file path'))
    parser.add_argument('-D', '--diag',
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")
    args = parser.parse_args()
    main(args)
