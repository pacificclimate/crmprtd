import time
from functools import wraps
import yaml
from pkg_resources import resource_stream
import logging
import logging.config


class Timer(object):
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.run_time = self.end - self.start


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


def common_script_arguments(parser):    # pragma: no cover
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string')
    parser.add_argument('-D', '--diag',
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")
    parser.add_argument('-L', '--log_conf',
                        default=None,
                        help=('YAML file to use to override the default '
                              'logging configuration'))
    parser.add_argument('-l', '--log_filename',
                        default=None,
                        help='Override the default log filename')
    parser.add_argument('-o', '--log_level',
                        choices=['DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        help=('Set log level: DEBUG, INFO, WARNING, ERROR, '
                              'CRITICAL.  Note that debug output by default '
                              'goes directly to file'))
    parser.add_argument('-m', '--error_email',
                        default=None,
                        help=('Override the default e-mail address to which '
                              'the program should report critical errors'))
    parser.add_argument('-C', '--cache_file',
                        help='Full path of file in which to put downloaded '
                              'observations')
    parser.add_argument('-i', '--input_file',
                        help='Input file to process')
    parser.add_argument('-d', '--cache_dir',
                        help='Directory in which to put the downloaded file')
    return parser


def common_auth_arguments(parser):     # pragma: no cover
    parser.add_argument('--auth_fname',
                        help="Yaml file with plaintext usernames/passwords")
    parser.add_argument('--auth_key',
                        help=("Top level key which user/pass are stored in "
                              "yaml file."))
    parser.add_argument('--username',
                        help=("The username for data requests. Overrides auth "
                              "file."))
    parser.add_argument('--password',
                        help=("The password for data requests. Overrides auth "
                              "file."))
    return parser


def setup_logging(log_conf, log_filename, error_email, log_level, name):
    if log_conf:
        with open(log_conf, 'rb') as f:
            base_config = yaml.load(f)
    else:
        base_config = yaml.load(resource_stream('crmprtd',
                                                '/data/logging.yaml'))

    if log_filename:
        base_config['handlers']['file']['filename'] = log_filename

    if error_email:
        base_config['handlers']['mail']['toaddrs'] = error_email

    if log_level:
        base_config['root']['level'] = log_level

    logging.config.dictConfig(base_config)
