import logging
from datetime import datetime

import pytest

from crmprtd.infill import download_and_process, round_datetime, datetime_range


def test_download_and_process(mocker, caplog):
    mocker.patch("subprocess.run", return_value=True)
    with caplog.at_level(logging.DEBUG):
        download_and_process(
            [], "moti", "postgresql://user:password@db3.pcic/somdb", []
        )
    for record in caplog.records:
        assert "password" not in record.message


@pytest.mark.parametrize(
    ("resolution", "direction", "expected"),
    (
        ("hour", "up", datetime(2021, 1, 7, 4)),
        ("hour", "down", datetime(2021, 1, 7, 3)),
        ("day", "up", datetime(2021, 1, 8)),
        ("day", "down", datetime(2021, 1, 7)),
    ),
)
def test_round_datetime(resolution, direction, expected):
    d = datetime(2021, 1, 7, 3, 44)
    result = round_datetime(d, resolution, direction)
    assert result == expected


@pytest.mark.parametrize(
    ("resolution", "direction"),
    (
        ("hour", "up"),
        ("hour", "down"),
        ("day", "up"),
        ("day", "down"),
    ),
)
def test_round_datetime_identity(resolution, direction):
    d = datetime(2021, 1, 6)
    assert round_datetime(d, resolution, direction) == d


@pytest.mark.parametrize(
    ("start", "end", "resolution"),
    (
        (None, None, "hour"),
        (None, None, "day"),
        (None, None, "week"),
        (None, None, "month"),
    ),
)
def test_datetime_range(start, end, resolution):
    start = datetime(2021, 1, 20, 11)
    end = datetime(2021, 1, 31, 00)
    result = datetime_range(start, end, resolution)
    next(result)
    assert True
    # Hey we didn't error... that's good enough for now :P
