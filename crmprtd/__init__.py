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
import logging
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pkg_resources import resource_stream
from collections import namedtuple
from itertools import tee
from crmprtd.align import align
from crmprtd.insert import insert


Row = namedtuple('Row', "time val variable_name unit network_name \
                         station_id lat lon")

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
    parser.add_argument('--chunk_size', type=int,
                        default=4096,
                        help='The size of observation chunks that will be '
                             'mass inserted into the database')
    parser.add_argument('--sample_size', type=int,
                        default=50,
                        help='Number of samples to be taken from observations '
                             'to determine which insertion strategy to use')
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


def get_insert_args(args):
    return subset_dict(vars(args), ['chunk_size', 'sample_size'])


def subset_dict(a_dict, keys_wanted):
    return {key: a_dict[key] for key in keys_wanted if key in a_dict}


def run_data_pipeline(download_func, normalize_func, download_args,
                      cache_file, connection_string, insert_args):
    '''Executes all stages of the data processing pipeline.

       Downloads the data, according to the download arguments
       provided (generally from the command line), normalizes the data
       based on the network's format. The the fuction send the
       normalized rows through the align and insert phases of the
       pipeline.
    '''
    download_iter = download_func(**download_args)

    if cache_file:
        download_iter, cache_iter = tee(download_iter)
        with open(cache_file, 'w') as f:
            for chunk in cache_iter:
                f.write(chunk)

    rows = [row for row in normalize_func(download_iter)]

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    observations = list(filter(lambda ob: ob is not None,
                               [align(sesh, row) for row in rows]))
    results = insert(sesh, observations, **insert_args)
    print(results)
