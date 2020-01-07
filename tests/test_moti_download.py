import datetime

import pytest

from crmprtd.moti.download import verify_date, download


def test_verify_date():
    assert verify_date('2020/01/01 00:00:00', None) == \
        datetime.datetime(2020, 1, 1)


@pytest.mark.parametrize(('datestring'), (
    ('not-a-datestring'),
    (None)
))
def test_verify_date_exception(datestring):
    default = 1
    warning = 'Parameter {} \'{}\' is undefined or unparseable. Using the '\
              'default \'{}\''.format('', datestring, default)
    with pytest.warns(UserWarning, match=warning):
        assert verify_date(datestring, default, '') == default


now = datetime.datetime.now()


@pytest.mark.parametrize('stime etime station_id expected'.split(), (
    # ('stime', 'etime', 'station_id', 'expected'),
    # (None, None, None, None),
    # (None, None, 'the_koots', None),
    (None, now, None, ValueError), #error
    # (None, now, 'the_koots', None),
    (now, None, None, ValueError), # error
    # (now, None, 'the_koots', None),
    (now, now, None, ValueError), # error
    # (now, now, 'the_koots', None)
))
def test_download(stime, etime, station_id, expected):
    with pytest.raises(expected):
        download('u', 'p', None, None,
                 stime, etime, station_id)
