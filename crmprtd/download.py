import sys
import time
import ftplib
import logging
import csv
from functools import wraps

import yaml


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


def ftp_connect(ReaderClass, host, path, log, auth=None):
    log.info('Fetching file from FTP')
    log.info('Listing.', extra={'host': host, 'path': path})

    user, password = (auth['u'], auth['p']) if auth else (None, None)

    try:
        ftpreader = ReaderClass(host, user,
                                password, path, log)
        log.info('Opened a connection to host', extra={'host': host})
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)

    return ftpreader


class FTPReader(object):
    '''Glue between the FTP class methods (which are callback based)
       and the csv.DictReader class (which is iteration based)
    '''

    def __init__(self):
        '''WAMR and WMB need to implement slight variats of this for their
        connections.
        '''
        raise NotImplementedError

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
    if username or password:
        return {'u': username, 'p': password}
    else:
        assert auth_file and auth_key, ("Must provide both the auth file "
                                        "and the key to use for this "
                                        "script (--auth_key)")
        with open(auth_file, 'r') as f:
            config = yaml.load(f)
        return {
            'u': config[auth_key]['username'],
            'p': config[auth_key]['password']
        }
