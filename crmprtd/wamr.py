import re
import sys
import logging
import logging.config
import csv
from pkg_resources import resource_stream
import ftplib

import pytz
from dateutil.parser import parse
import yaml
from pint import UnitRegistry

from crmprtd import retry
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

    # This variable is actually named wrong in WAMR's files
    row['PARAMETER'] = re.sub('WSPD_VECT', 'WSPD_SCLR', row['PARAMETER'])

    if row['PARAMETER'] not in variables:
        raise Exception('Could not find variable {} in the db'
                        .format(row['PARAMETER']))
    else:
        var = variables[row['PARAMETER']]

    # Parse the date
    d = parse(row['DATE_PST']).replace(tzinfo=tz)

    # Check/convert the unit if applicable
    val = float(row['REPORTED_VALUE'])
    src_unit = row['UNIT']
    dst_unit = var.unit

    # Hack the units. We shouldn't have to do this, but our units library
    # (pint) is kind of a pain when it comes to processing the % sign.
    # Let's just do a simple string replace and move on with our lives
    src_unit = re.sub('% RH', 'percent', row['UNIT'])
    dst_unit = re.sub('%', 'percent', dst_unit)

    if src_unit != dst_unit:
        log.debug("Source", extra={'value': val, 'unit': src_unit})
        try:
            val = Q_(val, ureg.parse_expression(src_unit))  # src
            val = val.to(dst_unit).magnitude  # dest
        except Exception:
            raise Exception(
                "Can't convert source unit {} to destination unit {}".format(
                    src_unit, dst_unit)
            )
        log.debug("Converted", extra={'value': val, 'unit': dst_unit})

    # Create and return the object
    return Obs(time=d, variable=var, history=hist, datum=val)


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


class FTPReader(object):  # pragma: no cover
    '''Glue between the FTP class methods (which are callback based)
       and the csv.DictReader class (which is iteration based)
    '''

    def __init__(self, host, user, password, data_path, log=None):
        self.filenames = []

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            con = ftplib.FTP(host)
            con.login(user, password)
            return con

        self.connection = ftp_connect_with_retry(host, user, password)

        def callback(line):
            self.filenames.append(line)

        self.connection.retrlines('NLST ' + data_path, callback)

    def csv_reader(self, log=None):
        # Just store the lines in memory
        # It's non-ideal but neither classes support coroutine send/yield
        if not log:
            log = logging.getLogger('__name__')

        lines = []

        def callback(line):
            lines.append(line)

        for filename in self.filenames:
            log.info("Downloading from file", extra={'file': filename})
            # FIXME: This line has some kind of race condition with this
            self.connection.retrlines('RETR {}'.format(filename), callback)

        r = csv.DictReader(lines)
        return r

    def __del__(self):
        try:
            self.connection.quit()
        except Exception:
            self.connection.close()


def file2rows(file_, log):
    try:
        reader = csv.DictReader(file_)
    except csv.Error as e:
        log.critical('Unable to load data from local file', exc_info=True)
        sys.exit(1)

    return [row for row in reader], reader.fieldnames


def ftp2rows(host, path, log):  # pragma: no cover
    log.info('Fetching file from FTP')
    log.info('Listing', extra={'host': host, 'path': path})

    try:
        ftpreader = FTPReader(host, None,
                              None, path, log)
        log.info('Opened a connection', extra={'host': host})
        reader = ftpreader.csv_reader(log)
        log.info('instantiated the reader and downloaded all of the data')
    except ftplib.all_errors as e:
        log.critical('Unable to load data from ftp source', exc_info=True)
        sys.exit(1)

    return [row for row in reader], reader.fieldnames
