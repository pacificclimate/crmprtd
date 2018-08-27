import sys
from importlib import import_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from argparse import ArgumentParser

from crmprtd.align import align
from crmprtd.insert import insert
from crmprtd import logging_args, setup_logging


def process_args(parser):
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string',
                        required=True)
    # FIXME: I do not think this arg gets used anywhere
    parser.add_argument('-D', '--diag',
                        default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")
    parser.add_argument('--sample_size', type=int,
                        default=50,
                        help='Number of samples to be taken from observations '
                             'when searching for duplicates '
                             'to determine which insertion strategy to use')
    parser.add_argument('-N', '--network',
                        choices=['ec', 'moti', 'wamr', 'wmb'],
                        help='The network from which the data is coming from. '
                             'The name will be used for a dynamic import of '
                             'the module\'s normalization function.')
    return parser


def get_data():
    for line in sys.stdin.buffer.readlines():
        yield line


def get_normalization_module(network):
    return import_module('crmprtd.{}.normalize'.format(network))


def create_history_mapping(sesh, rows):
    from pycds import History, Station, Network
    '''Create a names -> history object map for the set of stations that are
       contained in the rows
    '''
    # Each row (observation) is attributed with a station
    # individually, so start by creating a set of unique stations in
    # the file. Minimize round-trips to the database.
    stn_ids = {row.station_id for row in rows}

    def lookup_stn(ems_id):
        q = sesh.query(History).join(Station).join(Network)\
                .filter(Station.native_id == ems_id)
        return q.all()
    mapping = [(ems_id, lookup_stn(ems_id)) for ems_id in stn_ids]

    # Filter out EMS_IDs for which we have no station metadata
    return {ems_id: hist for ems_id, hist in mapping if hist}


def create_variable_mapping(sesh, rows):
    from pycds import Variable, Station, Network
    '''Create a names -> history object map for the set of observations that are
       contained in the rows
    '''
    var_names = {(row.variable_name, row.network_name) for row in rows}

    def lookup_var(v, n):
        q = sesh.query(Variable).join(Network)\
                .filter(Network.name == n).filter(Variable.name == v)
        return q.first()
    mapping = [(var_name, lookup_var(var_name, net_name)) for var_name, net_name in var_names]

    return {var_name: var_ for var_name, var_ in mapping if var_}


def process(connection_string, sample_size, network):
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

    download_iter = get_data()
    norm_mod = get_normalization_module(network)

    rows = [row for row in norm_mod.normalize(download_iter)]

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    history_mapping = create_history_mapping(sesh, rows)
    variable_mapping = create_variable_mapping(sesh, rows)
    observations = [ob for ob in [align(sesh, row) for row in rows] if ob]
    results = insert(sesh, observations, sample_size)
    log.info('Data insertion results', extra={'results': results})


def main():
    parser = ArgumentParser()
    parser = process_args(parser)
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd')

    process(args.connection_string, args.sample_size, args.network)


if __name__ == "__main__":
    main()
