import logging
from datetime import datetime

import pytz
from dateutil.parser import parse

from pycds import Network, Station, History, Obs, Variable

tz = pytz.timezone('Canada/Pacific')


def create_station_mapping(sesh, rows):
    '''Create a names -> history object map for the set of stations that are
       contained in the rows
    '''
    # Each row (observation) is attributed with a station
    # individually, so start by creating a set of unique stations in
    # the file. Minimize round-trips to the database.
    stn_ids = {row['EMS_ID'] for row in rows}

    def lookup_stn(ems_id):
        q = sesh.query(History).join(Station).join(Network)\
                .filter(Station.native_id == ems_id)
        # FIXME: Handle multiple history_ids and failed searches
        return q.first()
    mapping = [(ems_id, lookup_stn(ems_id)) for ems_id in stn_ids]

    # Filter out EMS_IDs for which we have no station metadata
    return {ems_id: hist for ems_id, hist in mapping if hist}


def create_variable_mapping(sesh, rows):
    '''Create a names -> history object map for the set of observations that are
       contained in the rows
    '''
    var_names = {row['PARAMETER'] for row in rows}

    def lookup_var(v):
        q = sesh.query(Variable).join(Network)\
                .filter(Network.name == 'ENV-AQN').filter(Variable.name == v)
        return q.first()
    mapping = [(var_name, lookup_var(var_name)) for var_name in var_names]

    return {var_name: var_ for var_name, var_ in mapping if var_}


def process_obs(sesh, row, log=None, histories={}, variables={}):
    """Take a list of dictionary based observations and return a list of
    pycds.Obs objects

    data - list of dictionaries given by csv.DictReader with keys:
    DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,
    RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,
    REPORTED_VALUE
    """
    if not log:
        log = logging.getLogger(__name__)

    if row['EMS_ID'] not in histories:
        raise Exception('Could not find station {EMS_ID}/{STATION_NAME}'
                        ' in the db'.format(**row))
    else:
        hist = histories[row['EMS_ID']]

    if row['PARAMETER'] not in variables:
        raise Exception('Could not find variable {} in the db'
                        .format(row['PARAMETER']))
    else:
        var = variables[row['PARAMETER']]

    # Parse the date
    d = parse(row['DATE_PST']).replace(tzinfo=tz)

    value = float(row['REPORTED_VALUE'])

    # Create and return the object
    return Obs(time=d, variable=var, history=hist, datum=value)


class DataLogger(object):
    def __init__(self, log=None):
        self.bad_rows = []
        self.bad_obs = []
        if not log:
            self.log = logging.getLogger(__name__)

    def add_row(self, data=None, reason=None):
        # handle single observations
        if type(data) == dict:
            data['reason'] = reason
            self.bad_rows.append(data)

    def archive(self, out_dir):
        """
        Archive the unsuccessfull additions in a manner that allows
        easy re-insertion attempts.

        Returns full path of output csv
        """
        import csv
        import os.path

        outcsv = os.path.join(out_dir, 'wamr_data_errors_' +
                      datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S') +
                              '.csv')

        with open(outcsv, 'wb') as f:
            order = 'DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,'\
                    'INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,'\
                    'STATUS_DESCRIPTION,REPORTED_VALUE'.split(',')
            w = csv.DictWriter(f, fieldnames=order)
            w.writeheader()
            w.writerows(self.data)

        return outcsv

    @property
    def data(self):
        import itertools
        for row in itertools.chain(self.bad_rows, self.bad_obs):
            yield row
