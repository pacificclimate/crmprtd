import logging

import pytz
from dateutil.parser import parse

from pycds import Network, Station, History, Obs, Variable

log = logging.getLogger(__name__)


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
        hist = q.first()
    return { ems_id: lookup_stn(ems_id) for ems_id in stn_ids }


def process_obs(sesh, rows, prefs):
    """Take a list of dictionary based observations and return a list of
    pycds.Obs objects

    data - list of dictionaries given by csv.DictReader with keys:
    DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,
    RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,
    REPORTED_VALUE
    """
    log.debug('In process_obs()')
    print('In process_obs()')
    tz = pytz.timezone('Canada/Pacific')
    network = sesh.query(Network).filter(Network.name == 'ENV-AQN').first()
    log.debug('Network', network)
    histories = create_station_mapping(sesh, rows)
    log.debug('Histories', histories)
    return

    for row in rows:
        hist = histories[row['STATION_NAME']]

        # Parse the date
        d = parse(row['DATE_PST']).replace(tzinfo=tz)

        # Find the variable
        q = sesh.query(Variable).filter(Network == network)\
                .filter(Variable.name == row['PARAMETER'])
        var = q.first()

        # Create and yield the object
        obs = Obs(time=d, vars=var, history=hist, network=network,
                  datum=row['REPORTED_VALUE'])
        #yield obs


class DataLogger(object):
    pass
