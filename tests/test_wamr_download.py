import pytest

from crmprtd.download import ftp_download


@pytest.mark.network
def test_wamr_download(capsys):
    ftp_download('ftp.env.gov.bc.ca/pub/outgoing/AIR/Hourly_Raw_Air_Data/'
                 'Meteorological/', auth=None, use_tls=False)
    captured = capsys.readouterr()
    assert captured
