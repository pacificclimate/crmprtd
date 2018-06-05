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
from crmprtd.wmb_dir.normalize import wmb_normalize

# Installed libraries
import yaml

def wmb_download(args):
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

    log.info('Starting WMB rtd')
    data = []

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
            ftpreader = FTPReader(args.ftp_server, auth['u'], auth['p'], args.ftp_file, log)
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
        with open(fname_out, 'w') as f_out:
            copier = csv.DictWriter(f_out, fieldnames = reader.fieldnames)
            copier.writeheader()
            copier.writerows(data)  # is this part of normalize?

    log.info('{0} observations read into memory'.format(len(data)))
    wmb_normalize(args, log, data)

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
