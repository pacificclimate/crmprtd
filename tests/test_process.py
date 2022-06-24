import pytz
import pytest
import logging
from datetime import datetime
from pkg_resources import resource_filename

from pycds import Network
from crmprtd.download import verify_date
from crmprtd.process import process


@pytest.mark.parametrize(
    ("start_date", "end_date", "num_inserts"),
    [
        ("2022/06/1", "2022/06/18", 197),
        ("June 18", None, 0),
        (None, "June 17 2022 10am", 0),
        (None, None, 197),
    ],
)
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_process_date(
    start_date, end_date, num_inserts, monkeypatch, caplog, crmp_session
):
    caplog.set_level(logging.INFO)

    utc = pytz.utc

    start_date = utc.localize(verify_date(start_date, datetime.min, "start date"))
    end_date = utc.localize(verify_date(end_date, datetime.max, "end date"))

    forestry_data = open(resource_filename("crmprtd", "data/forestry_data.xml"))
    monkeypatch.setattr("sys.stdin", forestry_data)

    crmp_session.add(Network(name="FLNRO-WMB"))
    crmp_session.commit()

    process(
        crmp_session.get_bind().url,
        50,
        "bc_forestry",
        start_date,
        end_date,
        False,
        True,
    )

    assert (
        sum(
            bool("Successfully inserted observations" in str(record))
            for record in caplog.records
        )
        == num_inserts
    )
