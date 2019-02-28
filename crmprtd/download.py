import os
import sys
import time
import ftplib
import logging
import csv
from functools import wraps
from tempfile import SpooledTemporaryFile

import yaml

log = logging.getLogger(__name__)


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


def ftp_connect(host, path, log, auth=None, filename=None, use_tls=True):
    log.info('Fetching file from FTP')
    log.info('Listing.', extra={'host': host, 'path': path})

    user, password = (auth['u'], auth['p']) if auth else (None, None)

    try:
        ftpreader = FTPReader(host, user, password, path, log,
                              filename, use_tls)
        log.info('Opened a connection to host', extra={'host': host})
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)

    return ftpreader


def ftp_download(ftp_path, ftp_file=None, auth=None, use_tls=True):
    log.info('Starting FTP Download')

    ftp_host, path = ftp_path.split('/', 1)

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(ftp_host, path, log, auth,
                                ftp_file, use_tls)

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
            for line in tempfile.readlines():
                sys.stdout.buffer.write(line.encode('utf-8'))

    except Exception as e:
        log.exception("Unable to process ftp")


class FTPReader(object):
    '''Glue between the FTP class methods (which are callback based)
       and the csv.DictReader class (which is iteration based)
    '''
    def __init__(self, host, user, password, data_path, log=None,
                 filename=None, use_tls=True):

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            if use_tls:
                return ftplib.FTP_TLS(host, user, password)
            else:
                con = ftplib.FTP(host)
                con.login(user, password)
                return con

        self.connection = ftp_connect_with_retry(host, user, password)

        if filename:
            self.filenames = [filename]
        else:
            self.filenames = []

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


def extract_auth(username, password, auth_file, auth_key):
    '''Extract auth information

    Use either the username/password provided or pull the info out from the
    provided yaml file
    '''
    def none_to_empty_string(s):
        return s if s else ''

    if username or password:
        return {
            'u': none_to_empty_string(username),
            'p': none_to_empty_string(password)
        }
    else:
        assert auth_file and auth_key, ("Must provide both the auth file "
                                        "and the key to use for this "
                                        "script (--auth_key)")
        auth_yaml = auth_file.read() if auth_file else None
        config = yaml.load(auth_yaml)
        return {
            'u': config[auth_key]['username'],
            'p': config[auth_key]['password']
        }
