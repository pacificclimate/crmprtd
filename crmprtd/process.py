import sys
from importlib import import_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from argparse import ArgumentParser

from crmprtd.align import align
from crmprtd.insert import insert
from crmprtd import logging_args, setup_logging


def process_args(parser): # pragma: no cover
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string',
                        required=True)
    parser.add_argument('-D', '--diag',
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")
    parser.add_argument('--sample_size', type=int,
                        default=50,
                        help='Number of samples to be taken from observations '
                             'when searching for duplicates '
                             'to determine which insertion strategy to use')
    parser.add_argument('-N', '--network',
                        choices=['bc_env_aq', 'bc_env_snow', 'bc_forestry',
                                 'bc_tran', 'bch', 'crd', 'ec', 'moti', 'wamr',
                                 'wmb'],
                        help='The network from which the data is coming from. '
                             'The name will be used for a dynamic import of '
                             'the module\'s normalization function.')
    return parser


def get_normalization_module(network):
    return import_module('crmprtd.{}.normalize'.format(network))


def process(connection_string, sample_size, network, is_diagnostic=False):
    '''Executes 3 stages of the data processing pipeline.

       Normalizes the data based on the network's format.
       The the fuction send the normalized rows through the align
       and insert phases of the pipeline.
    '''
    log = logging.getLogger('crmprtd')

    if network is None:
        log.error('No module name given, cannot continue pipeline',
                  extra={'network': network})
        raise Exception('No module name given')

    download_stream = sys.stdin.buffer
    norm_mod = get_normalization_module(network)

    rows = [row for row in norm_mod.normalize(download_stream)]

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    observations = [
        ob for ob in [align(sesh, row, is_diagnostic) for row in rows] if ob
    ]

    if is_diagnostic:
        for obs in observations:
            log.info(obs)
        return

    results = insert(sesh, observations, sample_size)
    log.info('Data insertion results', extra={
        'results': results, 'network': network
    })


def main(): # pragma: no cover
    parser = ArgumentParser()
    parser = process_args(parser)
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd')

    process(args.connection_string, args.sample_size, args.network, args.diag)


if __name__ == "__main__":
    main()
