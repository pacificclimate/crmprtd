import pytest
import datetime

from crmprtd.download import extract_auth, https_download, verify_date


@pytest.mark.parametrize(
    ("user", "password", "expected"),
    (
        ("foo", "bar", {"u": "foo", "p": "bar"}),
        ("foo", None, {"u": "foo", "p": ""}),
        (None, "bar", {"u": "", "p": "bar"}),
        (None, None, {"u": "user_from_file", "p": "pw_from_file"}),
    ),
)
def test_extract_auth(user, password, expected):
    yaml = """my_test:
  username: user_from_file
  password: pw_from_file
"""
    assert extract_auth(user, password, yaml, "my_test") == expected


def test_https_download(requests_mock, capsys):
    requests_mock.get("https://test.com", text="data")
    https_download("https://test.com")
    captured = capsys.readouterr()
    assert captured.out == "data"
    https_download("https://test.com", auth={"u": "foo", "p": "ignored"})
    assert captured.out == "data"


def test_https_download_404(requests_mock):
    requests_mock.register_uri("GET", "https://test.com", status_code=404)
    with pytest.raises(IOError):
        https_download("https://test.com")


@pytest.mark.parametrize(
    ("datestring", "default"),
    (("2020/01/01 00:00:00", None), ("2020/01/01", None), ("January 1 2020 0am", None)),
)
def test_verify_date(datestring, default):
    assert verify_date(datestring, default, "") == datetime.datetime(2020, 1, 1)


@pytest.mark.parametrize(("datestring"), (("not-a-datestring"), (None)))
def test_verify_date_exception(datestring):
    default = 1
    warning = (
        "Parameter {} '{}' is undefined or unparseable. Using the "
        "default '{}'".format("", datestring, default)
    )
    with pytest.warns(UserWarning, match=warning):
        assert verify_date(datestring, default, "") == default
