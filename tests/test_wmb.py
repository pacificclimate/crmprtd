import pytest
import pytz
import csv
from sqlalchemy import and_

from datetime import datetime, date
from io import StringIO

from pycds import Obs, History, Network, Station
from crmprtd.wmb import ObsProcessor, insert_obs, check_history, query_by_attribute
from crmprtd.wmb_exceptions import UniquenessError


@pytest.mark.parametrize(('val', 'hid', 'd', 'vars_id', 'expected'), [
    (2.7, 20, datetime(2016, 9, 13, 6, tzinfo=pytz.utc), 1, 4)
])
def test_insert_obs(test_session, val, hid, d, vars_id, expected):
    insert_obs(val, hid, d, vars_id, test_session)

    q = test_session.query(Obs)
    assert q.count() == expected

    result, = test_session.query(Obs.datum).filter(Obs.history_id == hid, Obs.time == d, Obs.vars_id == vars_id).first()
    assert result == val

    with pytest.raises(UniquenessError):
        insert_obs(val, hid, d, vars_id, test_session)

    with pytest.raises(Exception):
        insert_obs('test', hid, d, vars_id, test_session)


def test_check_and_insert_stations(test_session, test_data):
    o = ObsProcessor(test_session, test_data, 1000)

    # Create a set of stations where one of them already exists in the table
    stations = set()
    id, = test_session.query(Station.native_id).join(Network).filter(Network.id == o.network_id).first()
    stations.add(id)    # Existing station
    for i in range(3):  # New stations
        id += str(i)
        stations.add(id)

    q = test_session.query(Station)
    count = q.count()

    o.check_and_insert_stations(stations)

    q = test_session.query(Station)
    assert q.count() == count + 3

    for station in stations:
        q = test_session.query(Station).join(Network).filter(Station.native_id == station, Network.id == o.network_id)
        assert q.count() == 1


def test_check_history(test_session):
    lines = '''station_code,weather_date,precipitation
81974,2012090312,12,
81974,2012090312,10,
81974,2010090312,8
'''
    data = []
    f = StringIO(lines)
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

    o = ObsProcessor(test_session, data, 1000)

    arkham_asylum = History(id=258,
                            station_name='Arkham Asylum',
                            sdate='2012-09-02',
                            edate='2012-09-06')
    test_session.add(arkham_asylum)
    test_session.add(Station(native_id='81974', network=o.network, histories=[arkham_asylum]))

    q = test_session.query(History)
    count = q.count()

    native_id = ''
    native_id = row['station_code']
    for row in o.data:
        check_history(row, o.network, test_session)

    q = test_session.query(History)
    assert q.count() == count + 1

    q = test_session.query(History).join(Station).filter(Station.native_id == native_id)
    assert q.count() == 2

    # test error handle
    err_lines = '''station_code,weather_date,precipitation
1029,2012090312,12
'''
    err_data = []
    f = StringIO(err_lines)
    reader = csv.DictReader(f)
    for row in reader:
        err_data.append(row)

    copy_hist = History(station_name='FIVE MILE')
    test_session.add(copy_hist)
    test_session.add(Station(native_id='1029', network=o.network, histories=[copy_hist]))
    for row in err_data:
        check = check_history(row, o.network, test_session)

    assert check == None


def test_process(test_session, test_data):
    o = ObsProcessor(test_session, test_data, 1000)
    o.process()

    q = test_session.query(Obs)
    assert q.count() == 8

# on ice until can figure out a way to test excpeption that does not get raised
# def test_parse_time_error_handle(test_session):
#     lines = '''station_code,weather_date,precipitation
# 81974,3333333333,12,
# 81974,6666666666,10,
# 81974,7777777777,8
# '''
#     data = []
#     f = StringIO(lines)
#     reader = csv.DictReader(f)
#     for row in reader:
#         data.append(row)
#
#     #with pytest.raises(ValueError):
#     o = ObsProcessor(test_session, data, 1000)
#
#     assert 1 == 2

def test_datalogger(test_session, test_data):
    o = ObsProcessor(test_session, test_data, 1000)
    data = {'weather_date': '2018061488'}
    assert len(o.datalogger.bad_rows) == 0

    o.datalogger.add_row(data, reason='Add single row')
    assert len(o.datalogger.bad_rows) == 1

    o.datalogger.add_row(test_data, reason='Add five rows')
    assert len(o.datalogger.bad_rows) == 6

    date = datetime(2018, 6, 13)
    row = {'station_code': '1234567', 'weather_date': datetime.date(date), 'ec_precip': 4}
    var = 'ec_precip'
    o.datalogger.add_obs(row, var, reason='Can this handle obs')
    assert len(o.datalogger.bad_obs) == 1

    # fresh obs
    fresh_o = ObsProcessor(test_session, test_data, 1000)
    fresh_o.datalogger.add_row(test_data, reason='Observation')
    data_archive = o.datalogger.archive('/home/nrados/')    # need to get around this
    with open(data_archive, 'r') as f:
        row_count = 0
        for row in f:
            row_count += 1
        assert row_count == 8

def test_query_by_attribute(test_data):
    result_multiple = query_by_attribute(test_data, 'station_code', '11')
    assert len(result_multiple) == 5

    result_single = query_by_attribute(test_data, 'weather_date', '2018052711')
    assert len(result_single) == 1

def test_archive_station(test_session, test_data):
    o = ObsProcessor(test_session, test_data, 1000)
    check = o._archive_station('11')
    assert check == 5
