import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging, logging.config

from pycds.util import create_test_database
from pycds import Network, Station, Contact, History, Variable

def test_nested_transactions_1(session):
    fake_network = Network(name='Fake Network')

    try:
        logging.info('in try')
        with session.begin_nested():
            logging.info('in with')
            session.merge(fake_network)
            logging.info('added network')
    except Exception as e:
        logging.info('caught exception, raising')
        raise e

def test_nested_transactions_2(session):
    fake_network = Network(name='Fake Network')
    with session.begin_nested():
        logging.info('in with')
        session.add(fake_network)
        logging.info('added moti network')

def test_nested_transactions_3(session):
    fake_network = Network(name='Fake Network')
    try:
        session.begin_nested()
        session.add(fake_network)
    except:
        session.rollback()
    else:
        session.commit()
