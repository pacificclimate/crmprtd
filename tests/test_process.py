import sys
import io
import pytest
from lxml import etree

from .ec_data import hourly_bc_2016061115
from crmprtd.process import process


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [
        ("2016/06/06", "2016/07/06"),
        ("2016/01/01", None),
        (None, "2016/12/31"),
        (None, None),
    ],
)
def test_process_date(start_date, end_date, monkeypatch):
    process()
