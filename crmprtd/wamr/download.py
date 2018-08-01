import ftplib
import logging
import os

from tempfile import SpooledTemporaryFile

# Local
from crmprtd.download import retry, ftp_connect
from crmprtd.download import FTPReader


log = logging.getLogger(__name__)


def download(ftp_server, ftp_dir):
    log.info('Starting WAMR rtd')

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(WAMRFTPReader, ftp_server, ftp_dir,
                                log)

        with SpooledTemporaryFile(
                max_size=int(os.environ.get('CRMPRTD_MAX_CACHE', 2**20)),
                mode='r+') as tempfile:

            for filename in ftpreader.filenames:

                def callback(line):
                    tempfile.write('{}\n'.format(line))

                log.info("Downloading %s", filename)
                ftpreader.connection.retrlines('RETR {}'.format(filename),
                                               callback)

            tempfile.seek(0)
            return tempfile.readlines()

    except Exception:
        log.exception("Unable to process ftp")


class WAMRFTPReader(FTPReader):
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
