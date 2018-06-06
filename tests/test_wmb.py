import pytest
import pytz
import csv
from sqlalchemy import and_

from datetime import datetime
from io import StringIO

from pycds import Obs, History, Network, Station
from crmprtd.wmb import ObsProcessor, insert_obs, check_history


@pytest.mark.parametrize(('val', 'hid', 'd', 'vars_id', 'expected'), [
    (2.7, 20, datetime(2016, 9, 13, 6, tzinfo=pytz.utc), 1, 4)
])
def test_insert_obs(test_session, val, hid, d, vars_id, expected):
    insert_obs(val, hid, d, vars_id, test_session)

    q = test_session.query(Obs)
    assert q.count() == expected

    q = test_session.query(Obs.datum).filter(Obs.history_id == hid, Obs.time == d, Obs.vars_id == vars_id)
    result = next(iter(q[0]))
    assert result == val


def test_check_and_insert_stations(test_session, test_data):
    o = ObsProcessor(test_session, test_data, 1000)

    stations = set()
    id = 0
    q = test_session.query(Station.native_id).join(Network).filter(Network.id == o.network_id).first()
    id = q[0]
    stations.add(id)
    for i in range(3):
        id += str(i)
        stations.add(id)

    q = test_session.query(Station)
    count = q.count()

    o.check_and_insert_stations(stations)

    q = test_session.query(Station)
    assert q.count() == count + 3

    for station in stations:
        q = test_session.query(Station).join(Network).filter(and_(Station.native_id == station, Network.id == o.network_id))
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


def test_process(test_session, test_data):
    o = ObsProcessor(test_session, test_data, 1000)
    o.process()

    q = test_session.query(Obs)
    assert q.count() == 8
