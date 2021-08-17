import pytest

from crmprtd.infill import download_and_process


def test_download_and_process(mocker, caplog):
    mocker.patch('subprocess.run', return_value=True)
    with caplog.at_level(logging.DEBUG):
        download_and_process([], "moti", "postgresql://user:password/somdb", [])
    for record in caplog.records:
        assert "password" not in record.message
