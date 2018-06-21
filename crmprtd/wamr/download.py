import csv
import os
import ftplib

from datetime import datetime

# Local
from crmprtd import retry
from crmprtd.wamr import setup_logging
from crmprtd.wamr.normalize import normalize_file, normalize_ftp


def run(args):
    # Logging
    log = setup_logging(args.log_level, args.log, args.error_email)
    log.info('Starting WAMR rtd')

    # Output files
    if args.error_file:
        error_file = open(args.error_file, 'a')
    else:
        error_filename = 'wamr_errors_{}.csv'.format(datetime.strftime(
            datetime.now(), '%Y-%m-%dT%H-%M-%S'))
        error_file = open(os.path.join(args.cache_dir, error_filename), 'a')

    if args.input_file:
        # File
        with open(args.input_file) as f:
            normalize_file(f, args, error_file, log)
    else:
        # FTP
        ftpreader = ftp2rows(args.ftp_server, args.ftp_dir, log)
        normalize_ftp(ftpreader, error_file, args, log)


def ftp2rows(host, path, log):
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
