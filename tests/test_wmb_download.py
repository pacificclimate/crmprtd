import logging

import pytest

from crmprtd.download import ftp_download
from crmprtd import setup_logging


def test_setup_logging():
    setup_logging(None, 'mof.log', 'test@mail.com', 'CRITICAL', 'test')
    log = logging.getLogger('test')
    assert log.name == 'test'
    assert log.level == 0
    assert log.parent.level == 50


@pytest.mark.network
def test_wmb_download(capsys):
    ftp_download('BCFireweatherFTPp1.nrs.gov.bc.ca/',
                 'HourlyWeatherAllFields_WA.txt',
                 {'u': 'a_username', 'p': 'a_password'},
                 use_tls=True)
    captured = capsys.readouterr()
    assert captured
