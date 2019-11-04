from datetime import datetime

import pytest
import requests

from .swob_data import network_listing, day_listing, station_listing
from .swob_data import multi_xml_string
from crmprtd.ec_swob.download import match_date, get_url_list
from crmprtd.ec_swob.download import split_multi_xml_stream


@pytest.mark.parametrize(('url', 'expected'), (
    ('/20191018/station_id/', True),
    ('/20190101/station_id/', False),
    ('/url_without_any_date/', True)
))
def test_match_date(url, expected):
    date = datetime(2019, 10, 18)
    assert match_date(url, date) == expected


def test_get_url_list(requests_mock):
    def make_404(request):
        resp = requests.Response()
        resp.status_code = 404
        return resp

    requests_mock.add_matcher(make_404)
    requests_mock.register_uri(
        'GET',
        'https://dd.weather.gc.ca/observations/swob-ml/partners/bc-env-snow/',
        text=network_listing,
        status_code=200
    )
    requests_mock.register_uri(
        'GET',
        'https://dd.weather.gc.ca/observations/swob-ml/partners/bc-env-snow/'
        '20191015/',
        text=day_listing,
        status_code=200
    )
    requests_mock.register_uri(
        'GET',
        'https://dd.weather.gc.ca/observations/swob-ml/partners/bc-env-snow/'
        '20191015/1d06p/',
        text=station_listing,
        status_code=200
    )
    rv = get_url_list(
        'https://dd.weather.gc.ca/observations/swob-ml/partners/bc-env-snow/',
        datetime(2019, 10, 15, 1)
    )
    assert list(rv)


def test_split_multi_xml_stream():
    s = multi_xml_string
    strings = list(split_multi_xml_stream(s))
    assert len(strings) == 4
    assert strings[0] == \
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?><foo />'
