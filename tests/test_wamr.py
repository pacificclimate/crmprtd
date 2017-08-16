# coding=utf-8

import sys
from tempfile import TemporaryFile
from io import StringIO

import pytest

from crmprtd.wamr import rows2db, setup_logging, file2rows
from pycds import Obs, History, Network, Variable

# def test_insert(crmp_session):
#     pass


# def test_station_mapping(crmp_session):
#     pass


# def test_variable_mapping(crmp_session):
#     pass


# def test_process_obs(crmp_session):
#     pass
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


@pytest.mark.parametrize(('diagnostic', 'expected'), [
    (False, 3),
    (True, 0)
])
def test_rows2db(test_session, diagnostic, expected):

    log = setup_logging('DEBUG')

    lines = '''DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,REPORTED_VALUE
2017-05-21 17:00,0260011,Warfield Elementary Met_60,TEMP_MEAN,TEMP_MEAN,TEMP 10M,25.3,°C,1,n/a,Data Ok,25.3
2017-05-21 16:00,0260011,Warfield Elementary Met_60,TEMP_MEAN,TEMP_MEAN,TEMP 10M,26.65,°C,1,n/a,Data Ok,26.7
2017-05-21 15:00,0260011,Warfield Elementary Met_60,TEMP_MEAN,TEMP_MEAN,TEMP 10M,26.38,°C,1,n/a,Data Ok,26.4
2017-05-21 15:00,XXXX,Does not exist,TEMP_MEAN,TEMP_MEAN,TEMP 10M,26.38,°C,1,n/a,Data Ok,26.4
'''
    header_line, error_line = lines.splitlines()[0], lines.splitlines()[-1]

    with maybe_fake_file(lines) as f:
        rows, fieldnames = file2rows(f, log)

    with TemporaryFile('w+t') as error_file:
        rows2db(test_session, rows, error_file, log, diagnostic=diagnostic)

        error_file.seek(0)
        output = error_file.read()
        assert header_line in output
        assert error_line in output

    # Check that some obs were or were not inserted (depending on diagnostic mode)
    q = test_session.query(Obs).join(History).filter(History.station_name == 'Warfield Elementary')
    assert q.count() == expected


def test_rows2db_units_conversion(test_session):
    ''' Test that units are properly converted from the source data into the
        unit that is recorded in the databse
    '''
    sesh = test_session
    log = setup_logging('DEBUG')

    network = sesh.query(Network).filter(Network.name == 'ENV-AQN').first()
    # Define the units in the database to always be stored as degrees celsius
    sesh.add(Variable(name='TEMP_CELSIUS', unit='degC', network=network))
    sesh.commit()

    lines = '''DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,REPORTED_VALUE
2017-05-21 17:00,0260011,Warfield Elementary Met_60,TEMP_CELSIUS,TEMP_MEAN,TEMP 10M,32.0,°F,1,n/a,Data Ok,32.0
2017-05-21 16:00,0260011,Warfield Elementary Met_60,TEMP_CELSIUS,TEMP_MEAN,TEMP 10M,0.0,°C,1,n/a,Data Ok,0.0
2017-05-21 15:00,0260011,Warfield Elementary Met_60,TEMP_CELSIUS,TEMP_MEAN,TEMP 10M,273.15,°K,1,n/a,Data Ok,273.15
2017-05-21 15:00,0260011,Warfield Elementary Met_60,TEMP_CELSIUS,TEMP_MEAN,TEMP 10M,273.15,not_convertable,1,n/a,Data Ok,273.15
'''
    header_line, error_line = lines.splitlines()[0], lines.splitlines()[-1]

    with maybe_fake_file(lines) as f:
        rows, fieldnames = file2rows(f, log)

    with TemporaryFile('w+t') as error_file:
        rows2db(sesh, rows, error_file, log, diagnostic=False)

    q = sesh.query(Obs).join(History).filter(History.station_name == 'Warfield Elementary')

    obs = q.all()

    assert len(obs) == 3 # The not_conertable obs was not included

    for ob in q.all():
        assert ob.datum == pytest.approx(0, abs=1.0e-6)