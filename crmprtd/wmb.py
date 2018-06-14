import logging

from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from sqlalchemy import and_, or_

from pycds import Network, Station, Variable, History, Obs
from crmprtd.wmb_exceptions import InsertionError, UniquenessError

log = logging.getLogger(__name__)


class ObsProcessor:

    def __init__(self, sesh, data, prefs):
        """
        Take a list of dictionary based observations and do everything to
        insert into crmp database

        data - list of dictionaries given by csv.DictReader with keys
            "station_code",
            "weather_date",
            precipitation,
            temperature,
            relative_humidity,
            wind_speed,
            wind_direction,
            ffmc,
            isi,
            fwi,
            rn_1_pluvio1,
            snow_depth,
            snow_depth_quality,
            precip_pluvio1_status,
            precip_pluvio1_total,
            rn_1_pluvio2,
            precip_pluvio2_status,
            precip_pluvio2_total,
            rn_1_RIT,precip_RIT_Status,
            precip_RIT_total,
            precip_rgt,
            solar_radiation_LICOR,
            solar_radiation_CM3

        prefs - an object of type optparse.Values with attributes:
            connection_string, log,
            cache_dir, error_email
        raises: IOError, psycopg2.OperationalError
        """
        self._lines = 0
        self._unhandled_errors = 0
        self._line_errors = 0
        self._total_obs = 0
        self._inserted_obs = 0
        self._insert_errors = 0
        self._obs_in_db = 0

        self.sesh = sesh
        self.prefs = prefs
        self.datalogger = DataLogger()
        self.data = self._parse_times(data)
        self.data_vars = set(self.data[0].keys())
        self.network_id = self.sesh.query(
            Network.id).filter(Network.name == 'FLNRO-WMB')
        self.network = self.sesh.query(Network).filter(
            Network.id == self.network_id).first()

    def _parse_times(self, data):
        """
        Times are given in format YYYYMMDDHH, using 24 as a valid HH
        This must be converted to DD+1, HH=00 before being stored
        into a datetime instance
        """

        log.debug('parsing all dates')
        unparsable_times = []

        for obs in data:
            try:
                d = obs['weather_date'][:8]
                t = obs['weather_date'][-2:]
                dt = parse(d) + relativedelta(hours=+int(t))
                obs['weather_date'] = dt
            except ValueError as e:
                log.error('Unexpected values when parsing date: {0}'.format(
                    obs['weather_date']))
                self._line_errors += 1
                self._unhandled_errors += 1
                unparsable_times.append(obs)
                # remove observations from data later to keep loop indices
                continue

        # now is later...
        self.datalogger.add_row(unparsable_times, reason="Time Parsing")
        for obs in unparsable_times:
            data.remove(obs)

        log.info('Sucessfully parsed station dates'.format(
            len(unparsable_times)))
        return data

    def print_data(self):
        order = ['station_code', 'weather_date', 'precipitation',
                 'temperature', 'relative_humidity', 'wind_speed',
                 'wind_direction']
        for k in order:
            print(k + '\t|\t'),
        for obs in self.data:
            print('')
            for k in order:
                print(str(obs[k]) + '\t|\t')

    def process(self):
        """
        This function handles inserting all valid observations into
        the database.

        In order to avoid any fkey constraints, it starts by validating
        all the stations present in the data with those in the database
        and inserting if necessary.
        """

        # Check all stations
        self.stations = set()
        for obs in self.data:
            self.stations.add(obs['station_code'])

        log.info('Checked all stations')
        new_stations = self.check_and_insert_stations(self.stations)
        log.info('Inserted new station_ids: {0}'.format(new_stations))

        # determine valid csv vars -> valid db vars mapping
        self.db_vars = self._recordable_vars()
        log.info('Determined recordable variables')

        # Attempt to insert all observations, logging all errors
        log.info('Processing {0} lines...'.format(len(self.data)))
        for row in self.data:
            try:
                log.debug('Processing observation at station {s} '
                          'timestamp {t}'.format(s=row['station_code'],
                                                 t=row['weather_date']
                                                 ))

                self.process_row(row)

            except Exception as e:
                log.error('Error inserting observation at station '
                          '{s} timestamp {t} -> {e}'
                          .format(s=row['station_code'],
                                  t=row['weather_date'],
                                  e=e))
                self.datalogger.add_row(row, reason='Database/Interface Error')
            self._lines += 1

        summary = """Processed {0} total lines with {5} having line errors resulting in
                    {4} individual observations.
                    {2} of these were already in the database,
                    {3} had InserationErrors that will need to be handled, and
                    {1} Observations were inserted successfully
            """.format(self._lines,
                       self._inserted_obs,
                       self._obs_in_db,
                       self._insert_errors,
                       self._total_obs,
                       self._line_errors)
        log.info(summary)

        if self._unhandled_errors:
            data_archive = None
            try:
                data_archive = self.datalogger.archive(self.prefs.archive_dir)
            except:
                log.exception('Unable to save error archive')
            log.critical('''Errors occured in WMB real time daemon that require a human touch.
            Please consult the log file at {1}.
            Data has been archived at {0}
            '''.format(data_archive, self.prefs.log))

    def process_row(self, row):
        """
        This will take a single observation, parse the measurements, and
        attempt to insert into database.

        psycopg2 errors caught in caller:
            InterfaceError
            DatabaseError
            ->    DataError
            ->    OperationalError
            ->    IntegrityError
            ->    InternalError
            ->    ProgrammingError

        InserationErrors and UniquenessErrors are handled
        """

        # get history_id
        hid = check_history(row, self.network, self.sesh)
        log.debug('\tHistory id {0}'.format(hid))

        if hid is None:
            self._line_errors += 1
            self._unhandled_errors += 1
            self.datalogger.add_row(
                row, reason='Cannot find or create history_id')
            return None

        # insert the observation by variable
        d = row['weather_date']
        for var in self.db_vars.keys():
            try:
                # already made sure var exists in row, but just in case...
                if var not in row.keys():
                    continue

                if not row[var]:  # avoid possibly empty values
                    continue
                self._total_obs += 1

                insert_obs(row[var], hid, d, self.db_vars[var], self.sesh)
                self._inserted_obs += 1
                log.debug(
                    '\tInserted {0} with value {1}'.format(var, row[var]))

            except UniquenessError as e:
                log.debug(e)
                self._obs_in_db += 1
                continue

            except InsertionError as e:
                log.debug(
                    'Error inserting observation, rolling back: {e}'.format(
                        e=e))
                self._insert_errors += 1
                self.datalogger.add_obs(row, var, reason='InserationError')

    def check_and_insert_stations(self, stations):
        """
        This takes a set of station native id's, compares these with
        those already in the database and adds any that are not.
        """

        # create set of all stations in dl
        dl = set(stations)

        # query existing stations in database
        q = self.sesh.query(Station.native_id).filter(
            Station.network == self.network)
        db = set([record[0] for record in q])

        # determine new stations and add to db

        new_stations = dl.difference(db)
        log.info('New stations with native_ids: {}'.format(new_stations))
        for station in new_stations:
            log.debug('Station id {native_id} not in db'.format(
                native_id=station))
            self.sesh.begin_nested()
            try:
                stn = Station(native_id=station, network=self.network)
                self.sesh.add(stn)
            except Exception as e:
                self.sesh.rollback()
                log.error(
                    'Could not add station {native_id}, archiving data'.format(
                        native_id=station), e)
                self._unhandled_errors += 1
                self._archive_station(station)
            else:
                self.sesh.commit()
                log.debug('Added native id {native_id}'.format(
                    native_id=station))

        return new_stations

    def _archive_station(self, station):
        """
        This takes a station native_id and removes and archives all associated
        data
        """

        archive_data = query_by_attribute('station_code', station)
        for obs in archive_data:
            self.data.remove(obs)
        self.datalogger.add_row(archive_data,
                                reason='Unable to add entire station')

        return len(archive_data)

    def _recordable_vars(self):
        """
        This looks at what variables are provided in the download
        and compares it to what the database is able to accept.

        Returns a dictionary mapping dl vars to acceptable db vars
        """
        q = self.sesh.query(Variable.name, Variable.id).filter(
            Variable.network == self.network)
        d = {}
        for net_var_name, vars_id in q:
            if net_var_name in self.data_vars:
                d[net_var_name] = vars_id

        return d


def check_history(obs, network, sesh):
    """
    Checks to see if an active history_id exists for this observation or
    it not adds one.

    Returns the history_id if successful or None if not
    """

    # Search for history_id entries which match this station
    native_id = obs['station_code']
    hist = sesh.query(History.id).join(Station)\
                                 .filter(Station.native_id == native_id,
                                         Station.network == network)\
                                 .filter(and_(or_(
                                         History.sdate <= obs['weather_date'],
                                         History.sdate.is_(None)),
                                     or_(
                                         History.edate >= obs['weather_date'],
                                         History.edate.is_(None))))

    # If multiple results, handle error
    if hist.count() > 1:
        log.error(
            'Multiple valid history ids for station {0}'.format(native_id))
        return None

    record = hist.first()
    if record:
        log.debug('\tHistory ID found: {0}'.format(record[0]))
        return record[0]

    # No record found, create new one.
    log.debug('Creating meta_history entry for {}'.format(native_id))
    sesh.begin_nested()
    try:
        stn = sesh.query(Station).filter(Station.native_id ==
                                         native_id, Station.network == network)
        if stn.count() != 1:
            return None
        stn = stn.first()
        hist = History(station=stn)
        sesh.add(hist)
    except Exception as e:
        sesh.rollback()
        log.error(
            'Could not add meta_history entry for {}: {}'.format(native_id, e))
    else:
        sesh.commit()
        log.debug('Added meta_history entry {}'.format(hist.id))
        return hist.id

    # If we get this far, something has gone wrong
    return None


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
        log.error('Unable to convert value to Decimal: {0}'.format(e))
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
        log.debug(e)
        raise InsertionError(obs_time=d, datum=val,
                             vars_id=vars_id, hid=hid, e=e)

    # value does not exist in obs_raw, continue with insertion
    try:
        o = Obs(time=d, datum=val, vars_id=vars_id, history_id=hid)
        sesh.add(o)
        return
    except Exception as e:
        log.debug(e)
        raise InsertionError(obs_time=d, datum=val,
                             vars_id=vars_id, hid=hid, e=e)

    # Should have already returned success, failure, or exception by now...
    log.debug('Unknown Error')
    raise InsertionError(obs_time=d, datum=val, vars_id=vars_id, hid=hid)


def query_by_attribute(data, key, value):
    """
    Taking a list of dictionaries typically produced from a csv.DictReader
    class, this function returns all rows that have a key matching
    a particular value
    """

    results = []
    for row in data:
        if row[key] == value:
            results.append(row)
    return results


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

        with open(outcsv, 'wb') as f:
            w = csv.writer(f)
            w.writerow(order)
            for row in self.data:
                try:
                    w.writerow([row.get(k, '') for k in order])
                except Exception as e:
                    log.exception('Unable to archive row {0}'.format(row))
                    continue
        return outcsv

    @property
    def data(self):
        import itertools
        for row in itertools.chain(self.bad_rows, self.bad_obs):
            yield row
