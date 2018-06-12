from crmprtd.wmb.download import logging_setup

def test_logging_setup():
    log = logging_setup('mof.log', 'test@mail.com', 'INFO')
    assert log != None
