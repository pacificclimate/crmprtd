"""The crmprtd ("CRMP Real Time Daemon) package

This crmprtd package is package written to perform regular, periodic
weather data acquisition from a variety of government agencies
(i.e. "networks) for long-term climate monitoring.

CRMP stands for "Climate Related Monitoring Program", the iniative by
the province of BC to jointly pool the partners' weather data. RTD
stands for "real-time daemon"), an unfortunate name since data
acquisition does not happen in real time and its programs are never
run as a daemon (at most, they are run as hourly cron jobs). But, hey,
that's the name and who's gonna change it?

The package operates a data pipeline of four phases: Download,
Normalize, Align, and Insert. The Download and Normalize phases are
specific to each network's data formats and time freqency. The Align
and Insert are common across all networks.

Download: This phase consists of polling a specific network resource
(FTP/HTTP site), downloading and saving a file that contains plain
text weather observations. The resources required are access to the
network, resource URIs, authentication details, and storage. This
phase needs to be scheduled at regular intervals (depending on the
network), and may be parametrized by date if supported by the network
(i.e. some networks allow you to select dates in the recent past).

Normalize: This phase consists of performing network specific text
transformations and extraction of information to the weather
observations. This may include XML XSLT transformations, unit or
variable name rewrites according to mapping rules, etc. The input to
this phase is simply a file stream and the output is simply a stream
of tuples (time, val, variable name, unit, network name, station id, lat,
lon) in native types. The idea of this phase is that it requires no
access to the database, just network specific knowledge.

Align: This phase consists of performing database consistency checks
required to insert the incoming data records. Do the stations already
exist or do we need to create them? Do the variables exist or can we
create them? Etc. The input is a stream tuples and the output is a
stream of pycds.Obs objects. This phase is common to all networks.

Insert: This phase simply consists of doing a mass insert of
observations into the database. The phase needs to handle any unique
constraint errors, and track and report on the successes and
failures. This phase needs to manage the database transactions for
speed and reliability. This phase is common to all networks.
"""

import io
import time
import logging
import yaml
from pkg_resources import resource_stream
from collections import namedtuple
from itertools import tee


Row = namedtuple('Row', "time val variable_name unit network_name \
                         station_id lat lon")


class Timer(object):
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.run_time = self.end - self.start


def common_script_arguments(parser):    # pragma: no cover
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string')
    parser.add_argument('-D', '--diag',
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")
    parser.add_argument('-L', '--log_conf',
                        default=resource_stream(
                            'crmprtd', '/data/logging.yaml'),
                        help=('YAML file to use to override the default '
                              'logging configuration'))
    parser.add_argument('-l', '--log',
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
    return parser


def setup_logging(log_conf, log, error_email, log_level, name):
    log_c = yaml.load(log_conf)
    if log:
        log_c['handlers']['file']['filename'] = log
    else:
        log = log_c['handlers']['file']['filename']
    if error_email:
        log_c['handlers']['mail']['toaddrs'] = error_email
    logging.config.dictConfig(log_c)
    log = logging.getLogger(name)
    if log_level:
        log.setLevel(log_level)

    return log


def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
    """
    Lets you use an iterable (e.g. a generator) that yields
    bytestrings as a read-only input stream.

    The stream implements Python 3's newer I/O API (available in
    Python 2's io module).  For efficiency, the stream is buffered.

    From: goo.gl/Yxm5vz

    """
    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None

        def readable(self):
            return True

        def readinto(self, b):
            try:
                length = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:length], chunk[length:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0    # indicate EOF
    return io.BufferedReader(IterStream(), buffer_size=buffer_size)


def run_data_pipeline(download_func, normalize_func, download_args):
    '''Executes all stages of the data processing pipeline.

       Downloads the data, according to the download arguments
       provided (generally from the command line), normalizes the data
       based on the network's format. The the fuction send the
       normalized rows through the align and insert phases of the
       pipeline.

    '''
    args = download_args
    download_iter = download_func(args)

    if args.cache_file:
        download_iter, cache_iter = tee(download_iter)
        with open(args.cache_file, 'w') as f:
            for chunk in cache_iter:
                f.write(chunk)

    rows = [row for row in normalize_func(download_iter)]
    observations = [align(row) for row in rows]
    for ob in observations:
        print(obs)
    # insert(observations)
