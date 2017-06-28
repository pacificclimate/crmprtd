# coding=utf-8

from types import SimpleNamespace
from tempfile import NamedTemporaryFile, TemporaryFile, TemporaryDirectory
from io import StringIO

import pytest

from crmprtd.wamr import rows2db, setup_logging, file2rows
from pycds import Obs, History

# def test_insert(crmp_session):
#     pass


# def test_station_mapping(crmp_session):
#     pass


# def test_variable_mapping(crmp_session):
#     pass


# def test_process_obs(crmp_session):
#     pass


def test_rows2db(test_session):

    log = setup_logging('DEBUG')

    lines = '''DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,REPORTED_VALUE
2017-05-21 17:00,0260011,Warfield Elementary Met_60,TEMP_MEAN,TEMP_MEAN,TEMP 10M,25.3,°C,1,n/a,Data Ok,25.3
2017-05-21 16:00,0260011,Warfield Elementary Met_60,TEMP_MEAN,TEMP_MEAN,TEMP 10M,26.65,°C,1,n/a,Data Ok,26.7
2017-05-21 15:00,0260011,Warfield Elementary Met_60,TEMP_MEAN,TEMP_MEAN,TEMP 10M,26.38,°C,1,n/a,Data Ok,26.4
'''

    with StringIO(lines) as f:
        rows, fieldnames = file2rows(f, log)

    with TemporaryFile() as error_file:
        rows2db(test_session, rows, error_file, log, diagnostic=False)

    # Check that some obs were inserted
    q = test_session.query(Obs).join(History).filter(History.station_name == 'Warfield Elementary')
    assert q.count() == len(lines.splitlines()) - 1
