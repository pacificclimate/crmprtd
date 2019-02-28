import pytest

from crmprtd.wamr.download import download


@pytest.mark.network
def test_wamr_download(capsys):
    download('ftp.env.gov.bc.ca', 'pub/outgoing/AIR/Hourly_Raw_Air_Data/'
             'Meteorological/')
    captured = capsys.readouterr()
    assert captured
