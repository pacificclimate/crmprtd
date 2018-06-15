# Standard module
import sys
import csv
import logging
import logging.config
import os
import ftplib

# debug
from pkg_resources import resource_stream

# Local
from crmprtd import retry
from crmprtd.wmb.normalize import prepare

# Installed libraries
import yaml


def logging_setup(log, error_email, log_level):
    log_c = yaml.load(resource_stream('crmprtd', '/data/logging.yaml'))
    if log:
        log_c['handlers']['file']['filename'] = log
    else:
        log = log_c['handlers']['file']['filename']
    if error_email:
        log_c['handlers']['mail']['toaddrs'] = error_email
    logging.config.dictConfig(log_c)
    log = logging.getLogger('crmprtd.wmb')
    if log_level:
        log.setLevel(log_level)

    return log


def local_file_search(archive_file, archive_dir, log):
    # adjust to full path
    path = archive_file
    if archive_file[0] != '/':
        path = os.path.join(archive_dir, archive_file)
    log.info('Loading local file {0}'.format(path))

    try:
        with open(path) as f:
            log.debug('opened the local file')
            reader = csv.DictReader(f)
            return reader
    except IOError as e:
        log.exception('Unable to load data from local file')
        sys.exit(1)


def ftp_file_read(ftp_server, ftp_file, log, auth):
    # Fetch file from FTP and read into memory
    log.info('Fetching file from FTP')
    log.info('Downloading {}/{}'.format(ftp_server, ftp_file))

    try:
        ftpreader = FTPReader(ftp_server, auth['u'], auth['p'], ftp_file, log)
        log.info('Opened a connection to {}'.format(ftp_server))
        reader = ftpreader.csv_reader()
        log.info('instantiated the reader')
        return reader
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)


def run(args):
    # Setup logging
    log = logging_setup(args.log, args.error_email, args.log_level)
    log.info('Starting WMB rtd')

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
        reader = local_file_search(args.archive_file, args.archive_dir, log)
    # Or use FTP source
    else:
        reader = ftp_file_read(args.ftp_server, args.ftp_file, log, auth)

    prepare(args, log, reader)


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
