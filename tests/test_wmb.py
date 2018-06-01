import sys
import pytest
import pytz
import csv
import random
from sqlalchemy import and_

from datetime import datetime
from decimal import Decimal
from io import StringIO
from tempfile import TemporaryFile

from pycds import Obs, History, Network, Station
from crmprtd.wmb import ObsProcessor, insert_obs, check_history


@pytest.mark.parametrize(('val', 'hid', 'd', 'vars_id', 'expected'), [
    # It looks like the vars table is indexed?
    (2.7, 20, datetime(2016, 9, 13, 6, tzinfo=pytz.utc), Decimal(1), 4)
])
def test_insert_obs(test_session, val, hid, d, vars_id, expected):
    insert_obs(val, hid, d, vars_id, test_session)
    q = test_session.query(Obs)
    assert q.count() == expected
    # sanity check
    q = test_session.query(Obs).filter(Obs.datum == val, Obs.history_id == hid, Obs.time == d, Obs.vars_id == vars_id)
    assert q.count() == 1


@pytest.mark.parametrize(('pre_insert', 'post_insert', 'row_check'), [
    (6, 9, 1)
])
def test_check_and_insert_stations(test_session, pre_insert, post_insert, row_check):
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,2018052711,.00,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052712,.00,16.4,57,9.1,152,81.667679,2.166688,5.4912086,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052713,.00,16.9,54,11.3,185,82.228363,2.5902824,6.5181026,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052714,.00,17.8,53,10.5,185,82.773972,2.6630962,6.9062028,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052715,.00,17.4,50,8.2,161,83.291313,2.5341561,6.5958676,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0
'''
    data = []
    f = maybe_fake_file(lines)
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

    o = ObsProcessor(test_session, data, 1000)

    o.network_id = test_session.query(Network.id).filter(Network.name == 'FLNRO-WMB')
    o.network = test_session.query(Network).filter(Network.id == o.network_id).first()

    stations = set()
    id = 0
    q = test_session.query(Station.native_id).join(Network).filter(Network.id == o.network_id).first()
    for record in q:
        id = int(record)
        for i in range(4):
            id = id + i
            stations.add(str(id))

    q = test_session.query(Station)
    assert q.count() == pre_insert

    o.check_and_insert_stations(stations)

    q = test_session.query(Station)
    assert q.count() == post_insert

    test_val = random.sample(stations, 1)
    q = test_session.query(Station).join(Network).filter(and_(Station.native_id == test_val[0], Network.id == o.network_id))
    assert q.count() == row_check


@pytest.mark.parametrize(('post_insert', 'expected'), [
    (8, 3)
])
def test_check_history(test_session, post_insert, expected):
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
1047172,2012092511,.00,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
1047172,2018052712,.00,16.4,57,9.1,152,81.667679,2.166688,5.4912086,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
1047172,2011052713,.00,16.9,54,11.3,185,82.228363,2.5902824,6.5181026,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0s
'''
    data = []
    f = maybe_fake_file(lines)
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

    o = ObsProcessor(test_session, data, 1000)

    network_id = test_session.query(Network.id).filter(Network.name == 'EC_raw')
    network = test_session.query(Network).filter(Network.id == network_id).first()

    native_id = ''
    for row in o.data:
        check_history(row, network, test_session)
        native_id = row['station_code']

    q = test_session.query(History)
    assert q.count() == post_insert

    q = test_session.query(History).join(Station).filter(Station.native_id == native_id)
    assert q.count() == expected


@pytest.mark.parametrize(('expected'), [
    (8)
])
def test_process(test_session, expected):
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,2018052711,.00,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052712,.00,16.4,57,9.1,152,81.667679,2.166688,5.4912086,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052713,.00,16.9,54,11.3,185,82.228363,2.5902824,6.5181026,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052714,.00,17.8,53,10.5,185,82.773972,2.6630962,6.9062028,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052715,.00,17.4,50,8.2,161,83.291313,2.5341561,6.5958676,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0
'''
    data = []
    f = maybe_fake_file(lines)
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

    o = ObsProcessor(test_session, data, 1000)

    o.network_id = test_session.query(Network.id).filter(Network.name == 'FLNRO-WMB')
    o.network = test_session.query(Network).filter(Network.id == o.network_id).first()

    o.process()

    q = test_session.query(Obs)
    assert q.count() == expected


# taken from test_wamr.py, still need to figure out import
def maybe_fake_file(lines):
    # StringIO combined with csv.DictReader really don't like utf-8
    # Just use a temp file if we have to
    if sys.version_info.major < 3:
        f = TemporaryFile()
        f.write(lines)
        f.seek(0)
        return f
    else:
        return StringIO(lines)


def query_print(query):
    print("Query: %s\nResult:" % (str(query)))
    for record in query:
        print("\t%s" % record)
    print('------> END')
