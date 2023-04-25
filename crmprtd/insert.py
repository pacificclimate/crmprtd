"""insert.py
The insert module handles the Insert phase of the crmprtd
pipeline. This phase simply consists of doing a mass insert of
observations into the database. The phase needs to handle any unique
constraint errors, and track and report on the successes and
failures. This phase needs to manage the database transactions for
speed and reliability. This phase is common to all networks.
"""

from math import floor, log as mathlog
from sqlalchemy import and_
import logging
import time
from sqlalchemy.exc import IntegrityError
import random

from crmprtd.db_exceptions import InsertionError
from pycds import Obs


log = logging.getLogger(__name__)


class DBMetrics(object):
    """Keep track of database metrics during the insertion process."""

    def __init__(self, successes, skips, failures):
        self.successes = successes
        self.skips = skips
        self.failures = failures

    def __add__(self, another):
        return DBMetrics(
            self.successes + another.successes,
            self.skips + another.skips,
            self.failures + another.failures,
        )


class Timer(object):
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.run_time = self.end - self.start


def pow_two_chunk(num):
    return 2 ** floor(mathlog(num, 2))


def get_chunk_sizes(remainder):
    chunk_list = []
    while remainder != 0:
        chunk_size = pow_two_chunk(remainder)
        remainder -= chunk_size
        chunk_list.append(chunk_size)
    return chunk_list


def chunks(obs):
    pos = 0
    for chunk_size in get_chunk_sizes(len(obs)):
        yield obs[pos : pos + chunk_size]
        pos += chunk_size


def get_sample_indices(num_obs, sample_size):
    if sample_size > num_obs:
        sample_size = num_obs

    return random.sample(range(num_obs), sample_size)


def obs_exist(sesh, history_id, vars_id, time):
    q = sesh.query(Obs).filter(
        and_(Obs.history_id == history_id, Obs.vars_id == vars_id, Obs.time == time)
    )
    return q.count() > 0


def contains_all_duplicates(sesh, observations, sample_size):
    sample_obs = []
    sample_indices = get_sample_indices(len(observations), sample_size)

    for index in sample_indices:
        sample_obs.append(observations[index])

    for sample in sample_obs:
        if not obs_exist(sesh, sample.history_id, sample.vars_id, sample.time):
            return False

    return True


def insert_single_obs(sesh, obs):
    """Insert a single observation"""
    try:
        # Create a nested SAVEPOINT context manager to rollback to in the
        # event of unique constraint errors
        log.debug("New SAVEPOINT for single observation")
        with sesh.begin_nested():
            sesh.add(obs)
    except IntegrityError as e:
        log.debug(
            "Failure, observation already exists",
            extra={"observation": obs, "exception": e},
        )
        db_metrics = DBMetrics(0, 1, 0)
    except InsertionError as e:
        # TODO: InsertionError is an defined by crmprtd. It can't be raised by
        #   SQLAlchemy unless something very tricky is going on. Why is this here?
        log.warning(
            "Failure occured during insertion",
            extra={"observation": obs, "exception": e},
        )
        db_metrics = DBMetrics(0, 0, 1)
    else:
        log.info("Successfully inserted observations: 1")
        db_metrics = DBMetrics(1, 0, 0)
    sesh.commit()
    return db_metrics


def single_insert_strategy(sesh, observations):
    dbm = DBMetrics(0, 0, 0)
    for obs in observations:
        dbm += insert_single_obs(sesh, obs)
    return dbm


def split(tuple_):
    if len(tuple_) < 1:
        return (), ()
    elif len(tuple_) < 2:
        return (tuple_[0], ())
    else:
        i = int(floor(len(tuple_) / 2))
        return (tuple_[:i], tuple_[i:])


def bisect_insert_strategy(sesh, observations):
    """This function implements a recursive Obs insert strategy to
    handle unique constraint errors on members of the set. The
    strategy used is to optimistically attempt to insert the entire
    set and in the event of a unique constraint error, it will
    divide the set into two and try again on each set (which will
    presumably have a lower probability of failing).

    In the degenerative case (all observations are duplicates), this
    strategy will require up to n *additional* transactions,
    but in the optimal case it reduces the transactions to a constant
    1.
    """
    log.debug("Begin mass observation insertion", extra={"num_obs": len(observations)})

    # Base cases
    if len(observations) < 1:
        return DBMetrics(0, 0, 0)
    elif len(observations) == 1:
        return insert_single_obs(sesh, observations[0])
    # The happy case: add everything at once
    else:
        try:
            with sesh.begin_nested():
                log.debug("New SAVEPOINT", extra={"num_obs": len(observations)})
                sesh.add_all(observations)
        except IntegrityError:
            log.debug("Failed, splitting observations.")
            sesh.rollback()

            a, b = split(observations)
            dbm_a = bisect_insert_strategy(sesh, a)
            dbm_b = bisect_insert_strategy(sesh, b)
            return dbm_a + dbm_b
        else:
            log.info(
                f"Successfully inserted observations: {len(observations)}",
                extra={"num_obs": len(observations)},
            )
            db_metrics = DBMetrics(len(observations), 0, 0)
        sesh.commit()
        return db_metrics


def insert(sesh, observations, sample_size):
    """
    Insert a collection of observations.

    :param sesh: SQLAlchemy database session
    :param observations: Obs objects to insert
    :param sample_size: Size of sample of observations to use to test if all duplicates.
    :return: dict with information about insertions
    """

    # First ensure that all pending objects (on which observations may depend) are
    # in the database.
    sesh.commit()

    if contains_all_duplicates(sesh, observations, sample_size):
        log.info("Using Single Insert Strategy")
        with Timer() as tmr:
            dbm = single_insert_strategy(sesh, observations)

    else:
        log.info("Using Chunk + Bisection Strategy")
        with Timer() as tmr:
            dbm = DBMetrics(0, 0, 0)
            for chunk in chunks(observations):
                dbm += bisect_insert_strategy(sesh, chunk)

    log.info("Data insertion complete")
    return {
        "successes": dbm.successes,
        "skips": dbm.skips,
        "failures": dbm.failures,
        "insertions_per_sec": round(dbm.successes / tmr.run_time, 2),
    }
