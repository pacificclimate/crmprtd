import pytest

from crmprtd.download import extract_auth, https_download


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
