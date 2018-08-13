import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_

from pycds import Obs
from crmprtd.db_exceptions import InsertionError, UniquenessError

log = logging.getLogger(__name__)


def insert_obs(val, hid, d, vars_id, sesh):
    """
    This takes an individual observation and inserts
    into obs_raw using the provided history_id, datetime, and variable id.
    We also need to differentiate between and error violating uniqueness
    and other errors that will require archiving the data.
    Uniqueness constrained by: history_id , vars_id , obs_time
    psycopg2.IntegrityError handles uniqueness, fkey,...
    Returns obs_raw_id on success, UniquenessError if already exists,
    or InsertionError on failure.
    """

    try:
        val = Decimal(val)
    except Exception as e:
        log.error('Unable to convert value to Decimal', extra={'exception': e})
        raise InsertionError(obs_time=d, datum=val,
                             vars_id=vars_id, hid=hid, e=e)

    # Check to see if this entry will be unique
    try:
        q = sesh.query(Obs.id).filter(
            and_(Obs.history_id == hid, Obs.vars_id == vars_id, Obs.time == d))
        if q.count() > 0:
            raise UniquenessError(q.first())
    except UniquenessError as e:
        log.debug(e)
        raise e
    except Exception as e:
        log.error(e)
        raise InsertionError(obs_time=d, datum=val,
                             vars_id=vars_id, hid=hid, e=e)

    # value does not exist in obs_raw, continue with insertion
    try:
        o = Obs(time=d, datum=val, vars_id=vars_id, history_id=hid)
        sesh.add(o)
        return
    except Exception as e:
        log.error(e)
        raise InsertionError(obs_time=d, datum=val,
                             vars_id=vars_id, hid=hid, e=e)

    # Should have already returned success, failure, or exception by now...
    log.error('Unknown Error')
    raise InsertionError(obs_time=d, datum=val, vars_id=vars_id, hid=hid)


class DataLogger:
    """
    The datalogger is used to keep track of 2 types of unsuccessful
    observations with their associated data:
        -bad observations: used when unable to find or create a station_id or
                           history_id, or parse observation time
        -bad values: when an individual value cannot be inserted into obs_raw
    """

    def __init__(self):
        self.bad_rows = []
        self.bad_obs = []

    def add_row(self, data=None, reason=None):
        # handle single observations
        if type(data) == dict:
            data['reason'] = reason
            # convert dt back to original format
            if type(data['weather_date']) == datetime:
                data['weather_date'] = datetime.strftime(
                    data['weather_date'], '%Y%m%d%H')
            self.bad_rows.append(data)

        # handle multiple observations as a list
        if type(data) == list:
            for row in data:
                row['reason'] = reason
                # convert dt back to original format
                if type(row['weather_date']) == datetime:
                    row['weather_date'] = datetime.strftime(
                        row['weather_date'], '%Y%m%d%H')
                self.bad_rows.append(row)

    def add_obs(self, obs, var, reason=None):
        """
        Recreate dictionary entry using only applicable variable
        """

        self.bad_obs.append({'station_code': obs['station_code'],
                             'weather_date': datetime.strftime(
                             obs['weather_date'], '%Y%m%d%H'),
                             var: obs[var], 'reason': reason
                             })

    def archive(self, out_dir):
        """
        Archive the unsuccessfull additions in a manner that allows
        easy re-insertion attempts.
        Returns full path of output csv
        """
        import csv
        import os.path

        outcsv = os.path.join(out_dir, 'wmb_data_errors_' +
                              datetime.strftime(datetime.now(),
                                                '%Y-%m-%dT%H-%M-%S') + '.csv')

        order = ['reason',
                 'station_code',
                 'weather_date',
                 'precipitation',
                 'temperature',
                 'relative_humidity',
                 'wind_speed',
                 'wind_direction',
                 'ffmc',
                 'isi',
                 'fwi',
                 'rn_1_pluvio1',
                 'snow_depth',
                 'snow_depth_quality',
                 'precip_pluvio1_status',
                 'precip_pluvio1_total',
                 'rn_1_pluvio2',
                 'precip_pluvio2_status',
                 'precip_pluvio2_total',
                 'rn_1_RIT',
                 'precip_RIT_Status',
                 'precip_RIT_total',
                 'precip_rgt',
                 'solar_radiation_LICOR',
                 'solar_radiation_CM3']

        with open(outcsv, 'w') as f:
            w = csv.writer(f)
            w.writerow(order)
            for row in self.data:
                try:
                    w.writerow([row.get(k, '') for k in order])
                except Exception as e:
                    log.exception('Unable to archive row', extra={'row': row})
                    continue
        return outcsv

    @property
    def data(self):
        import itertools
        for row in itertools.chain(self.bad_rows, self.bad_obs):
            yield row
