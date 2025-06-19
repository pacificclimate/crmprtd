import io
from datetime import datetime

import pytest

from .swob_data import multi_xml_bytes
from crmprtd.networks.ec_swob.download import match_date, get_url_list
from crmprtd.networks.ec_swob.download import split_multi_xml_stream, match_swob_xml_url


@pytest.mark.parametrize(
    ("url", "expected"),
    (
        ("/20191018/station_id/", True),
        ("/20190101/station_id/", False),
        ("/url_without_any_date/", True),
    ),
)
def test_match_date(url, expected):
    date = datetime(2019, 10, 18)
    assert match_date(url, date) == expected


def test_get_url_list(swob_urls):
    rv = get_url_list(
        "https://dd.weather.gc.ca/observations/swob-ml/partners/bc-env-snow/",
        datetime(2019, 10, 15, 1),
    )
    assert list(rv)


def test_split_multi_xml_stream():
    stream = io.BytesIO(multi_xml_bytes)
    strings = list(split_multi_xml_stream(stream))
    assert len(strings) == 4
    assert (
        strings[0].getvalue()
        == b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<foo />
"""
    )
    assert isinstance(strings[0], io.IOBase)


@pytest.mark.parametrize(
    ("url", "expected"),
    (
        (
            "https://dd.weather.gc.ca/observations/swob-ml/partners/dfo-ccg-lighthouse/20220525/boat_bluff/20220525T0530Z_DFO-CCG_SWOB_1060901.xml",
            True,
        ),
        (
            "https://dd.weather.gc.ca/observations/swob-ml/partners/bc-tran/20220526/11191/2022-05-25-0500-bc-tran-11191-AUTO-swob.xml",
            True,
        ),
        (
            "https://dd.weather.gc.ca/observations/swob-ml/partners/bc-tran/20220526/11191/2021-04-20-0300-bc-tran-11191-AUTO-swob.xml",
            False,
        ),
    ),
)
def test_match_swob_xml_url(url, expected):
    date = datetime(2022, 5, 25, 5)
    assert expected == bool(match_swob_xml_url(url, date))
