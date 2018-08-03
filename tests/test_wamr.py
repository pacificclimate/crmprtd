# coding=utf-8

import sys
from tempfile import TemporaryFile
from io import StringIO

from crmprtd.wamr import DataLogger

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


def test_datalogger_no_args():
    dl = DataLogger(None)
    assert dl.log is not None
