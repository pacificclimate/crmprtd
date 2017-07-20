# coding=utf-8

import sys
from tempfile import TemporaryFile
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

    def maybe_fake_file():
        # StringIO combined with csv.DictReader really don't like utf-8
        # Just use a temp file if we have to
        if sys.version_info.major < 3:
            f = TemporaryFile()
            f.write(lines)
            f.seek(0)
            return f
        else:
            return StringIO(lines)

    with maybe_fake_file() as f:
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
