import datetime

import pytest

import crmprtd.download_utils
from crmprtd.networks.moti.download import download


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
url = "https://prdoas5.apps.th.gov.bc.ca/saw-data/sawr7110"


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
    mocker.patch("crmprtd.download_utils.https_download")
    # Default time arguments are the "present" time at the time
    # download() is run. Since this is not predictable, we need to
    # mock out datetime.utcnow() to give us a deterministic time to
    # test against.
    mocker.patch("crmprtd.networks.moti.download.utcnow", return_value=now)
    download("u", "p", None, None, stime, etime, station_id, url)
    crmprtd.download_utils.https_download.assert_called_once()
    call_args, _ = crmprtd.download_utils.https_download.call_args
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
        download("u", "p", None, None, stime, etime, station_id, url)
        assert "Please either specify" in e.message


def test_download_too_long():
    etime = "2020/01/01 00:00:00"
    stime = "2019/12/01 00:01:01"
    station_id = "over_the_rainbow"
    with pytest.raises(ValueError) as e:
        download("u", "p", None, None, stime, etime, station_id, url)
        assert "however requests longer than 7" in e.message
