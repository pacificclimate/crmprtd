# Standard module
import sys
import csv
import logging
import logging.config
import os
import ftplib
from tempfile import SpooledTemporaryFile

# Local
from crmprtd import retry
from crmprtd.wmb.normalize import prepare

# Installed libraries
import yaml


def download(args):
    log = logging.getLogger(__name__)
    log.info('Starting WMB rtd')

    # Pull auth from args
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

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(args.ftp_server, args.ftp_file, log, auth)

        with SpooledTemporaryFile(max_size=2048, mode='r+') as tempfile:
            def callback(line):
                tempfile.write('{}\n'.format(line))

            log.info("Downloading %s", ftpreader.filename)
            ftpreader.connection.retrlines('RETR {}'.format(ftpreader.filename),
                                           callback)

            tempfile.seek(0)
            yield tempfile

    except Exception:
        log.critical("Unable to process ftp")


def ftp_connect(host, path, log, auth):
    log.info('Fetching file from FTP')
    log.info('Listing {}/{}'.format(host, path))

    try:
        ftpreader = FTPReader(host, auth['u'],
                              auth['p'], path, log)
        log.info('Opened a connection to {}'.format(host))
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)

    return ftpreader


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
