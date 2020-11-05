import os
from shutil import copyfile
from pkg_resources import resource_filename
from datetime import datetime
from operator import gt, eq

import pytest

from crmprtd.bc_hydro.download import temp_filename, download_relevant_bch_zipfiles


class FakeFTPConnection(object):
    def get(self, remote_filename, file_path):
        testfile = resource_filename("crmprtd", "tests/data/PCIC_BCHhourly_201103.zip")
        copyfile(testfile, file_path)


def test_temp_filename():
    with temp_filename() as fname:
        assert os.path.exists(fname)
    assert not os.path.exists(fname)


@pytest.mark.parametrize(
    "start end op".split(),
    (
        (datetime(2020, 10, 31), datetime(2020, 11, 5), gt),
        (datetime(2019, 1, 1), datetime(2020, 1, 1), eq),  # out of range dates
    ),
)
def test_download_relevant_bch_zipfiles(start, end, op, capsys):
    download_relevant_bch_zipfiles(
        start, end, FakeFTPConnection(), "PCIC_BCHhourly_201103.zip"
    )
    out, _ = capsys.readouterr()
    assert op(len(out), 0)


def test_download_relevant_bch_zipfiles_no_match():
    assert not download_relevant_bch_zipfiles(
        None, None, None, "PCIC_BC.........whocares.zip"
    )
