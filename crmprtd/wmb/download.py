# Standard module
import os
import logging
import logging.config
import ftplib
from tempfile import SpooledTemporaryFile

# Local
from crmprtd.download import retry, ftp_connect
from crmprtd.download import FTPReader, extract_auth


log = logging.getLogger(__name__)


def download(username, password, auth_fname, auth_key, ftp_server, ftp_file):
    log.info('Starting WMB rtd')

    auth_yaml = open(auth_fname, 'r').read() if auth_fname else None
    auth = extract_auth(username, password, auth_yaml, auth_key)

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(WMBFTPReader, ftp_server, ftp_file,
                                log, auth)

        with SpooledTemporaryFile(
                max_size=int(os.environ.get('CRMPRTD_MAX_CACHE', 2**20)),
                mode='r+') as tempfile:
            def callback(line):
                tempfile.write('{}\n'.format(line))

            for filename in ftpreader.filenames:
                log.info("Downloading %s", filename)
                ftpreader.connection.retrlines('RETR {}'
                                               .format(filename),
                                               callback)

            tempfile.seek(0)
            return tempfile.readlines()

    except Exception as e:
        log.exception("Unable to process ftp")


class WMBFTPReader(FTPReader):
    '''Glue between the FTP_TLS class methods (which are callback based)
       and the csv.DictReader class (which is iteration based)
    '''

    def __init__(self, host, user, password, filename, log=None):
        self.filenames = [filename]

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            return ftplib.FTP_TLS(host, user, password)

        self.connection = ftp_connect_with_retry(host, user, password)
