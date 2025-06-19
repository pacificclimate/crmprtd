from crmprtd import setup_logging
import logging


def test_setup_logging():
    setup_logging(None, "mof.log", "test@mail.com", "CRITICAL", "test")
    log = logging.getLogger("test")
    assert log.name == "test"
    assert log.level == 0
    assert log.parent.level == 50
