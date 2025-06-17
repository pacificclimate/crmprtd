import logging
import logging.config

from pycds import Network


def test_nested_transactions_1(crmp_session):
    fake_network = Network(name="Fake Network")

    try:
        logging.debug("in try")
        with crmp_session.begin_nested():
            logging.debug("in with")
            crmp_session.merge(fake_network)
            logging.debug("added network")
    except Exception as e:
        logging.debug("caught exception, raising")
        raise e


def test_nested_transactions_2(crmp_session):
    fake_network = Network(name="Fake Network")
    with crmp_session.begin_nested():
        logging.debug("in with")
        crmp_session.add(fake_network)
        logging.debug("added moti network")


def test_nested_transactions_3(crmp_session):
    fake_network = Network(name="Fake Network")
    try:
        crmp_session.begin_nested()
        crmp_session.add(fake_network)
    except Exception:
        crmp_session.rollback()
    else:
        crmp_session.commit()
