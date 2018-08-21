import sys
from importlib import import_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from argparse import ArgumentParser

from crmprtd.align import align
from crmprtd.insert import insert


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


def get_stdin():
    data = []
    for line in sys.stdin:
        # this retrieves the network name
        if "Network module name:" in line:
            line = line.strip('\n')
            network = line[21:]
        # allows logging from download phase
        elif 'asctime' in line and 'levelname' in line:
            line = line.strip('\n')
            print(line)
        else:
            data.append(line)

    return network, data


def get_normalization_module(network):
    return import_module('crmprtd.{}.normalize'.format(network))


def process(connection_string, sample_size):
    '''Executes 3 stages of the data processing pipeline.

       Normalizes the data based on the network's format.
       The the fuction send the normalized rows through the align
       and insert phases of the pipeline.
    '''
    network, download_iter = get_stdin()
    norm_mod = get_normalization_module(network)

    rows = [row for row in norm_mod.normalize(download_iter)]

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    observations = [ob for ob in [align(sesh, row) for row in rows] if ob]
    results = insert(sesh, observations, sample_size)

    log = logging.getLogger(__name__)
    log.info('Data insertion results', extra={'results': results})


if __name__ == "__main__":
    parser = ArgumentParser()
    parser = process_args(parser)
    args = parser.parse_args()

    process(args.connection_string, args.sample_size)
