import datetime

import pytest

import crmprtd.download
from crmprtd.moti.download import verify_date, download


def test_verify_date():
    assert verify_date("2020/01/01 00:00:00", None) == datetime.datetime(2020, 1, 1)


@pytest.mark.parametrize(("datestring"), (("not-a-datestring"), (None)))
def test_verify_date_exception(datestring):
    default = 1
    warning = (
        "Parameter {} '{}' is undefined or unparseable. Using the "
        "default '{}'".format("", datestring, default)
    )
    with pytest.warns(UserWarning, match=warning):
        assert verify_date(datestring, default, "") == default


now = datetime.datetime.now().replace(microsecond=0)
one_hour_ago = now - datetime.timedelta(seconds=3600)
now_string = now.strftime("%Y/%m/%d %H:%M:%S")
moti_fmt = "%Y-%m-%d/%H"
defaults = {
    "request": "historic",
    "station": "the_koots",
    "from": one_hour_ago.strftime(moti_fmt),
    "to": now.strftime(moti_fmt),
}


@pytest.mark.parametrize(
    "stime etime station_id expected_payload".split(),
    (
        # ('stime', 'etime', 'station_id', 'expected'),
        (None, None, None, {}),
        (None, None, "the_koots", {}),
        (None, now, "the_koots", defaults),
        (now, None, "the_koots", defaults),
        (
            now_string,
            now_string,
            "the_koots",
            {
                "request": "historic",
                "station": "the_koots",
                "from": now.strftime(moti_fmt),
                "to": now.strftime(moti_fmt),
            },
        ),
    ),
)
@pytest.mark.filterwarnings("ignore:Parameter")
def test_download(stime, etime, station_id, expected_payload, mocker):
    # We don't need/want to test the actually https request going out
    # so let's just mock that call and ensure that it gets called with
    # the expected arguments
    mocker.patch("crmprtd.download.https_download")
    # Default time arguments are the "present" time at the time
    # download() is run. Since this is not predictable, we need to
    # mock out datetime.utcnow() to give us a deterministic time to
    # test against.
    mocker.patch("crmprtd.moti.download.utcnow", return_value=now)
    download("u", "p", None, None, stime, etime, station_id)
    crmprtd.download.https_download.assert_called_once()
    call_args, _ = crmprtd.download.https_download.call_args
    _, _, _, _, payload = call_args
    assert payload == expected_payload


@pytest.mark.parametrize(
    "stime etime".split(),
    (
        (None, now),
        (now, None),
        (now, now),
    ),
)
def test_download_bad_args(stime, etime):
    """download() should raise a ValueError if it receives *any* time
    parameters, but not a station_id
    """
    station_id = None
    with pytest.raises(ValueError) as e:
        download("u", "p", None, None, stime, etime, station_id)
        assert "Please either specify" in e.message


def test_download_too_long():
    etime = "2020/01/01 00:00:00"
    stime = "2019/12/01 00:01:01"
    station_id = "over_the_rainbow"
    with pytest.raises(ValueError) as e:
        download("u", "p", None, None, stime, etime, station_id)
        assert "however requests longer than 7" in e.message
