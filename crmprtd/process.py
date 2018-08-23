import sys
from importlib import import_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from argparse import ArgumentParser
import pickle

from crmprtd.align import align
from crmprtd.insert import insert
from crmprtd import logging_args, setup_logging


def process_args(parser):
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string')
    # FIXME: I do not think this arg gets used anywhere
    parser.add_argument('-D', '--diag',
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")
    parser.add_argument('--sample_size', type=int,
                        default=50,
                        help='Number of samples to be taken from observations '
                             'when searching for duplicates '
                             'to determine which insertion strategy to use')
    return parser


def get_network():
    '''First line in stdout should contain a string with the network name.
       This name corresponds to the module name that needs to be imported
       dynamically.
    '''
    network = pickle.load(sys.stdin.buffer)
    if "Network module name:" in network:
        network = network.strip('\n')
        return network[21:]
    else:
        return None


def get_data():
    data = None
    # gather until end of file
    try:
        data = pickle.load(sys.stdin.buffer)
    except EOFError:
        pass

    t = type(data)
    if t == list:
        for datum in data:
            yield datum
    elif t == bytes:
        yield data


def get_normalization_module(network):
    return import_module('crmprtd.{}.normalize'.format(network))


def process(connection_string, sample_size):
    '''Executes 3 stages of the data processing pipeline.

       Normalizes the data based on the network's format.
       The the fuction send the normalized rows through the align
       and insert phases of the pipeline.
    '''
    log = logging.getLogger('crmprtd')
    network = get_network()
    if network is None:
        log.error('No module name given, cannot continue pipeline',
                  extra={'network': network})
        raise Exception('No module name given')

    download_iter = get_data()
    norm_mod = get_normalization_module(network)

    rows = [row for row in norm_mod.normalize(download_iter)]

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    observations = [ob for ob in [align(sesh, row) for row in rows] if ob]
    results = insert(sesh, observations, sample_size)
    log.info('Data insertion results', extra={'results': results})


if __name__ == "__main__":
    parser = ArgumentParser()
    parser = process_args(parser)
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd')

    process(args.connection_string, args.sample_size)
