import sys
import io
import os
import re
import pytz
import pytest
import logging
from datetime import datetime
from lxml import etree

from crmprtd.download import verify_date
from crmprtd.process import process


@pytest.mark.parametrize(
    ("start_date", "end_date", "num_obs"),
    [
        ("2022/06/1", "2022/06/18", 1643),
        ("June 18", None, 0),
        (None, "June 17 2022 10am", 0),
        (None, None, 1643),
    ],
)
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_process_date(start_date, end_date, num_obs, monkeypatch, caplog):

    caplog.set_level(logging.INFO)

    utc = pytz.utc

    start_date = utc.localize(verify_date(start_date, datetime.min, "start date"))
    end_date = utc.localize(verify_date(end_date, datetime.max, "end date"))

    script_dir = os.path.dirname(__file__)
    forestry_data = open(
        os.path.join(script_dir, "..", "crmprtd", "data", "forestry_data")
    )

    monkeypatch.setattr("sys.stdin", forestry_data)

    process(
        "postgresql://monsoon.pcic.uvic.ca:5432/crmp",
        50,
        "bc_forestry",
        start_date,
        end_date,
        True,
    )

    assert (
        sum(
            bool(re.search("<pycds.Obs object at 0x[a-z0-9]+>", str(record)))
            for record in caplog.records
        )
        == num_obs
    )
