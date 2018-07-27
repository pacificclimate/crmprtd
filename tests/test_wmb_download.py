from crmprtd import setup_logging
from pkg_resources import resource_stream


def test_setup_logging():
    log = setup_logging(resource_stream('crmprtd', '/data/logging.yaml'),
                        'mof.log', 'test@mail.com', 'INFO', 'crmprtd.wmb')
    assert log.name == 'crmprtd.wmb'
    assert log.level == 20
