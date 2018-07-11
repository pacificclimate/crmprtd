import csv
import sys
import ftplib
import logging
import os

from tempfile import SpooledTemporaryFile

# Local
from crmprtd import retry


def download(args):
    log = logging.getLogger(__name__)
    log.info('Starting WAMR rtd')

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(args.ftp_server, args.ftp_dir, log)

        for filename in ftpreader.filenames:
            with SpooledTemporaryFile(
                    max_size=int(os.environ.get('CRMPRTD_MAX_CACHE', 2**20)),
                    mode='r+') as tempfile:

                def callback(line):
                    tempfile.write('{}\n'.format(line))

                log.info("Downloading %s", filename)
                ftpreader.connection.retrlines('RETR {}'.format(filename),
                                               callback)

                tempfile.seek(0)
                yield tempfile

    except Exception:
        log.critical("Unable to process ftp")


def ftp_connect(host, path, log):
    log.info('Fetching file from FTP')
    log.info('Listing {}/{}'.format(host, path))

    try:
        ftpreader = FTPReader(host, None,
                              None, path, log)
        log.info('Opened a connection to {}'.format(host))
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)

    return ftpreader


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
        except Exception:
            self.connection.close()
