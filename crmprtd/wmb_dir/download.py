# Standard module
import sys
import csv
import logging, logging.config
import os
import ftplib

from datetime import datetime

# debug
from pkg_resources import resource_stream
# Local
from crmprtd import retry
from crmprtd.wmb_dir.normalize import prepare

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
    path = args.archive_file
    if args.archive_file[0] != '/':
        path = os.path.join(args.archive_dir, args.archive_file)
    log.info('Loading local file {0}'.format(path))

    # open and read into data
    data = []
    try:
        with open(path) as f:
            log.debug('opened the local file')
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
            return data
    except IOError as e:
        log.exception('Unable to load data from local file')
        sys.exit(1)


def ftp_file_search(ftp_server, ftp_file, log, auth, cache_dir):
    # Fetch file from FTP and read into memory
    log.info('Fetching file from FTP')
    log.info('Downloading {}/{}'.format(ftp_server, ftp_file))

    data = []
    try:
        ftpreader = FTPReader(ftp_server, auth['u'], auth['p'], ftp_file, log)
        log.info('Opened a connection to {}'.format(ftp_server))
        reader = ftpreader.csv_reader()
        for row in reader:
            data.append(row)
        log.info('instantiated the reader and processed all rows')
        save_file(reader, cache_dir, data)
        return data
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)


def save_file(reader, cache_dir, data):
    # save the downloaded file
    fname_out = os.path.join(cache_dir, 'wmb_download' + datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S') + '.csv')
    with open(fname_out, 'w') as f_out:
        copier = csv.DictWriter(f_out, fieldnames = reader.fieldnames)
        copier.writeheader()
        copier.writerows(data)


def run(args):
    # Setup logging
    log = logging_setup(args.log, args.error_email, args.log_level)
    log.info('Starting WMB rtd')

    # Pull auth from file or command line
    if args.username or args.password:
        auth = {'u':args.username, 'p':args.password}
    else:
        assert args.auth and args.auth_key, "Must provide both the auth file and the key to use for this script (--auth_key)"
        with open(args.auth, 'r') as f:
            config = yaml.load(f)
        auth = {'u':config[args.auth_key]['username'], 'p':config[args.auth_key]['password']}

    # Check for local file source
    if args.archive_file:
        data = local_file_search(args.archive_file, args.archive_dir, log)
    # Or use FTP source
    else:
        data = ftp_file_search(args.ftp_server, args.ftp_file, log, auth, args.cache_dir)

    log.info('{0} observations read into memory'.format(len(data)))
    prepare(args, log, data)


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
        except:
            self.connection.close()
