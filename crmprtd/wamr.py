import logging

import pytz
from dateutil.parser import parse

from pycds import Network, Station, History, Obs, Variable


class ObsProcessor(object):
    def __init__(self, sesh, data, prefs):
        """Take a list of dictionary based observations and do everything to
        insert into crmp database

        data - list of dictionaries given by csv.DictReader with keys:
        DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,
        RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,
        REPORTED_VALUE
        """
        pass


def create_station_mapping(sesh, rows):
    '''Create a names -> history object map for the set of stations that are
       contained in the rows
    '''
    # Each row (observation) is attributed with a station
    # individually, so start by creating a set of unique stations in
    # the file. Minimize round-trips to the database.
    stn_ids = { row['EMS_ID'] for row in rows }

    def lookup_stn(ems_id):
        q = sesh.query(History).join(Station).join(Network)\
                .filter(Station.native_id == ems_id)
        # FIXME: Handle multiple history_ids and failed searches
        return q.first()
    mapping = [ (ems_id, lookup_stn(ems_id)) for ems_id in stn_ids ]

    # Filter out EMS_IDs for which we have no station metadata
    return { ems_id: hist for ems_id, hist in mapping if hist }


def process_obs(sesh, rows, log=None):
    """Take a list of dictionary based observations and return a list of
    pycds.Obs objects

    data - list of dictionaries given by csv.DictReader with keys:
    DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,
    RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,
    REPORTED_VALUE
    """
    if not log:
        log = logging.getLogger(__name__)
    log.debug('In process_obs()')
    print('In process_obs()')
    tz = pytz.timezone('Canada/Pacific')
    network = sesh.query(Network).filter(Network.name == 'ENV-AQN').first()
    log.debug('Network %s', network)
    histories = create_station_mapping(sesh, rows)
    log.debug('Histories %s', histories)

    errors = []

    for row in rows:

        if row['EMS_ID'] not in histories:
            log.debug('Could not find station {EMS_ID}/{STATION_NAME} in the db'.format(**row))
            errors.append(row)
            continue

        hist = histories[row['EMS_ID']]

        # Find the variable
        q = sesh.query(Variable).filter(Network == network)\
                .filter(Variable.name == row['PARAMETER'])
        var = q.first()

        if not var:
            log.debug('Could not find variable {} in the db'.format(row['PARAMETER']))
            errors.append(row)
            continue

        # Parse the date
        d = parse(row['DATE_PST']).replace(tzinfo=tz)

        # Create and yield the object
        obs = Obs(time=d, vars=var, history=hist, network=network,
                  datum=row['REPORTED_VALUE'])
        log.debug(obs)
        print(obs)
        sesh.add(obs)


class DataLogger(object):
    pass
