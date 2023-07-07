import os
from shutil import copyfile
from pkg_resources import resource_filename
from datetime import datetime
from operator import gt, eq

import pytest

from crmprtd.networks.bc_hydro.download import (
    temp_filename,
    download_relevant_bch_zipfiles,
)


class FakeFTPConnection(object):
    def get(self, remote_filename, file_path):
        testfile = resource_filename("crmprtd", "tests/data/PCIC_BCHhourly_201103.zip")
        copyfile(testfile, file_path)


def test_temp_filename():
    with temp_filename() as fname:
        assert os.path.exists(fname)
    assert not os.path.exists(fname)


@pytest.mark.parametrize(
    "start end op fname".split(),
    (
        (
            datetime(2020, 10, 31),
            datetime(2020, 11, 5),
            gt,
            "PCIC_BCHhourly_201103.zip",
        ),
        (
            datetime(2019, 1, 1),
            datetime(2020, 1, 1),
            eq,
            "PCIC_BCHhourly_201103.zip",
        ),  # out of range dates
        # test for pattern matching; dates irrellevant
        (datetime.min, datetime.max, gt, "PCIC_230220.zip"),
        (datetime.min, datetime.max, gt, "PCIC_BCHhourly_200421.zip"),
        (
            datetime.min,
            datetime.max,
            gt,
            "2021-05-18_20-31-44.177_0000.PCIC_BCHhourly_210518.zip",
        ),
    ),
)
def test_download_relevant_bch_zipfiles(start, end, op, fname, capsys):
    download_relevant_bch_zipfiles(start, end, FakeFTPConnection(), fname)
    out, _ = capsys.readouterr()
    assert op(len(out), 0)


def test_download_relevant_bch_zipfiles_no_match():
    assert not download_relevant_bch_zipfiles(
        None, None, None, "PCIC_BC.........whocares.zip"
    )
