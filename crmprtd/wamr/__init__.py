import re
import sys
import logging
import logging.config
import csv

import pytz
from dateutil.parser import parse
from pint import UnitRegistry

from crmprtd.db import mass_insert_obs
from pycds import Network, Station, History, Obs, Variable
from crmprtd import Timer

tz = pytz.timezone('Canada/Pacific')
ureg = UnitRegistry()
Q_ = ureg.Quantity
for def_ in (
        "degreeC = degC; offset: 273.15",
        "degreeF = 5 / 9 * kelvin; offset: 255.372222",
        "degreeK = degK; offset: 0"
):
    ureg.define(def_)


class DataLogger(object):
    def __init__(self, log=None):
        self.bad_rows = []
        self.bad_obs = []
        if not log:
            self.log = logging.getLogger(__name__)

    def add_row(self, data=None, reason=None):
        # handle single observations
        data['reason'] = reason
        self.bad_rows.append(data)

    def archive(self, out_file):
        """
        Archive the unsuccessfull additions in a manner that allows
        easy re-insertion attempts.
        """
        order = 'DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,'\
                'INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,'\
                'STATUS_DESCRIPTION,REPORTED_VALUE,reason'.split(',')
        w = csv.DictWriter(out_file, fieldnames=order)
        w.writeheader()
        w.writerows(self.data)

        return

    @property
    def data(self):
        import itertools
        for row in itertools.chain(self.bad_rows, self.bad_obs):
            yield row


def rows2db(sesh, rows, error_file, log, diagnostic=False):
    '''
    Args:
        sesh (sqlalchemy.Session): A session with the crmp database
        rows (list):
        error_file (file):
        log (logging.Logger):

    '''
    dl = DataLogger(log)

    sesh.begin_nested()

    try:
        log.info('Processing observations')
        histories = create_station_mapping(sesh, rows)
        variables = create_variable_mapping(sesh, rows)

        obs = []
        for row in rows:
            try:
                obs.append(process_obs(sesh, row, log, histories, variables))
            except Exception as e:
                dl.add_row(row, e.args[0])

        log.info("Starting a mass insertion", extra={'num_obs': len(obs)})
        with Timer() as tmr:
            n_insertions = mass_insert_obs(sesh, obs, log)

        log.info("Data processed and inserted",
                 extra={'num_insertions': n_insertions,
                        'insertions_per_sec': (n_insertions/tmr.run_time)})

        if diagnostic:
            log.info('Diagnostic mode, rolling back all transactions')
            sesh.rollback()
        else:
            log.info('Commiting the sesh')
            sesh.commit()

    # FIXME: sqlalchemy.exc.OperationalError? (cannot connect to db)
    # sqlalchemy.exc.InternalError (read-only transaction)
    except Exception as e:
        dl.add_row(rows, 'preproc error')
        sesh.rollback()
        data_archive = dl.archive(error_file)
        log.critical('Error data preprocessing. See logfile.',
                     extra={'data_archive': data_archive})
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()

    dl.archive(error_file)


def file2rows(file_, log):
    try:
        reader = csv.DictReader(file_)
    except csv.Error as e:
        log.critical('Unable to load data from local file', exc_info=True)
        sys.exit(1)

    return [row for row in reader], reader.fieldnames
