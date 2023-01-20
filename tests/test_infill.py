import crmprtd.infill
import logging
from datetime import datetime
from subprocess import PIPE

import pytest
from unittest.mock import call, MagicMock

from crmprtd.infill import (
    download_and_process,
    round_datetime,
    datetime_range,
    chain_subprocesses,
)


# !! IMPORTANT !!
#
# Because `crmprtd.infill` imports `subprocesses.run` with `from subprocesses import run`
# (and not `import subprocesses`), we must mock `crmprtd.infill.run` and NOT
# `subprocesses.run`. If you mock the wrong `run` then you don't catch the calls and the
# commands actually get run. Potentially nasty. And counterintuitive.


def mock_run(mocker):
    return_value = MagicMock()
    return_value.stdout = "foo"
    mocker.patch("crmprtd.infill.run", return_value=return_value)
    return return_value


@pytest.mark.parametrize(
    # NB: Only use harmless operations to test this in case mocking of `run` is wrong!
    "commands, final_destination",
    [
        ([["ls", "-la"]], None),
        ([["ls", "-la"], ["sort"]], None),
        ([["ls", "-la"], ["sort"], ["wc", "-l"]], None),
    ],
)
def test_chain_subprocesses(commands, final_destination, mocker):
    return_value = mock_run(mocker)
    chain_subprocesses(commands, final_destination)
    expected_calls = [
        call(
            cmd,
            stdout=PIPE if i != len(commands) - 1 else final_destination,
            input=None if i == 0 else return_value.stdout,
        )
        for i, cmd in enumerate(commands)
    ]
    assert crmprtd.infill.run.call_args_list == expected_calls
    crmprtd.infill.run.reset_mock()


@pytest.mark.parametrize(
    "network_name, cache_filename, connection_string, expected_commands",
    [
        # Do nothing
        ("netwerk", None, None, []),
        # Download and cache only
        ("netwerk", "filename", None, ["crmprtd_download"]),
        # Download and process only
        ("netwerk", None, "dsn", ["crmprtd_download", "crmprtd_process"]),
        # Download, cache and process
        ("netwerk", "filename", "dsn", ["crmprtd_download", "tee", "crmprtd_process"]),
    ],
)
def test_download_and_process_choreography(
    network_name, cache_filename, connection_string, expected_commands, mocker
):
    mocker.patch("crmprtd.infill.chain_subprocesses", return_value=True)
    download_and_process(
        network_name=network_name,
        log_args=["--log_args"],
        download_args=["--download_args"],
        cache_filename=cache_filename,
        connection_string=connection_string,
        dry_run=False,
    )

    call_args = crmprtd.infill.chain_subprocesses.call_args
    commands = [arg[0] for arg in call_args.args[0]]
    assert commands == expected_commands

    final_destination = call_args.kwargs["final_destination"]
    if not cache_filename or connection_string:
        assert final_destination is None
    else:
        assert final_destination is not None


def test_download_and_process_security(mocker, caplog):
    mock_run(mocker)
    with caplog.at_level(logging.DEBUG):
        download_and_process(
            "moti",
            [],
            [],
            connection_string="postgresql://user:password@db.pcic/somdb",
            dry_run=False,
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
