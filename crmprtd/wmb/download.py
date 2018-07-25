# Standard module
import os
import logging
import logging.config
import ftplib
from tempfile import SpooledTemporaryFile

# Local
from crmprtd.download import retry, ftp_connect
from crmprtd.download import FTPReader

# Installed libraries
import yaml


log = logging.getLogger(__name__)


def download(args):
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
        ftpreader = ftp_connect(WMBFTPReader, args.ftp_server, args.ftp_file,
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
            yield tempfile

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
