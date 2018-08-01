import pytest
import pytz
import csv
import logging

from datetime import datetime
from io import StringIO

from pycds import Obs, History, Network, Station
from crmprtd.wmb import insert_obs
from crmprtd.wmb_exceptions import UniquenessError, InsertionError


@pytest.mark.parametrize(('val', 'hid', 'd', 'vars_id', 'expected'), [
    (2.7, 20, datetime(2016, 9, 13, 6, tzinfo=pytz.utc), 1, 4)
])
def test_insert_obs(test_session, val, hid, d, vars_id, expected):
    insert_obs(val, hid, d, vars_id, test_session)

    q = test_session.query(Obs)
    assert q.count() == expected

    result, = test_session.query(Obs.datum).filter(
        Obs.history_id == hid, Obs.time == d, Obs.vars_id == vars_id).first()
    assert result == val


def test_insert_obs_uniqness_error(test_session):
    val = 3.0
    hid = 21
    d = datetime(2017, 6, 17, 6, tzinfo=pytz.utc)
    vars_id = 1

    insert_obs(val, hid, d, vars_id, test_session)
    with pytest.raises(UniquenessError):
        insert_obs(val, hid, d, vars_id, test_session)


def test_insert_obs_insertion_errror(test_session):
    val = 'not_a_val'
    hid = 20
    d = datetime(2016, 9, 13, 6, tzinfo=pytz.utc)
    vars_id = 1
    with pytest.raises(InsertionError):
        insert_obs(val, hid, d, vars_id, test_session)


class ArgsForTest(object):
    '''Used by test_process_unhandled_errors to mimic arguments
    '''

    def __init__(self, archive_dir=None):
        self.archive_dir = archive_dir
        self.log = logging.getLogger(__name__)
