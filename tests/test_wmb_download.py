from crmprtd.wmb import setup_logging


def test_setup_logging():
    log = setup_logging('mof.log', 'test@mail.com', 'INFO')
    assert log.name == 'crmprtd.wmb'
    assert log.level == 20
