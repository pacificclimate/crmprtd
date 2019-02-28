import os
import logging

import pytest

from crmprtd.download import ftp_download, extract_auth
from crmprtd import setup_logging


def test_setup_logging():
    setup_logging(None, 'mof.log', 'test@mail.com', 'CRITICAL', 'test')
    log = logging.getLogger('test')
    assert log.name == 'test'
    assert log.level == 0
    assert log.parent.level == 50


@pytest.mark.network
def test_wmb_download(capsys):
    auth_fname = os.environ.get('CRMPRTD_AUTH', 'auth.yaml')
    auth_file = open(auth_fname, 'r')
    auth = extract_auth(None, None, auth_file, 'wmb')
    ftp_download('BCFireweatherFTPp1.nrs.gov.bc.ca/',
                 'HourlyWeatherAllFields_WA.txt',
                 auth,
                 use_tls=True)
    captured = capsys.readouterr()
    assert captured
