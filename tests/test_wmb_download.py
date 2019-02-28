import logging

import pytest

from crmprtd.wmb.download import download
from crmprtd import setup_logging

def test_setup_logging():
    setup_logging(None, 'mof.log', 'test@mail.com', 'CRITICAL', 'test')
    log = logging.getLogger('test')
    assert log.name == 'test'
    assert log.level == 0
    assert log.parent.level == 50


@pytest.mark.network
def test_wmb_download(capsys):
    download(None, None, 'real_auth.yaml', 'wmb',
             'BCFireweatherFTPp1.nrs.gov.bc.ca',
             'HourlyWeatherAllFields_WA.txt'
    )
    captured = capsys.readouterr()
    assert captured
