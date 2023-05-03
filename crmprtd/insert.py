"""insert.py
The insert module handles the Insert phase of the crmprtd
pipeline. This phase simply consists of doing a mass insert of
observations into the database. The phase needs to handle any unique
constraint errors, and track and report on the successes and
failures. This phase needs to manage the database transactions for
speed and reliability. This phase is common to all networks.
"""

from math import floor, log as mathlog
import logging
import time
import random

from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, DBAPIError

from crmprtd.constants import InsertStrategy
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


def max_power_of_two(num):
    return 2 ** floor(mathlog(num, 2))


def get_bisection_chunk_sizes(remainder):
    chunk_list = []
    while remainder != 0:
        chunk_size = max_power_of_two(remainder)
        remainder -= chunk_size
        chunk_list.append(chunk_size)
    return chunk_list


def bisection_chunks(obs):
    pos = 0
    for chunk_size in get_bisection_chunk_sizes(len(obs)):
        yield obs[pos : pos + chunk_size]
        pos += chunk_size


def fixed_length_chunks(a, chunk_size):
    """
    Chunk a list into pieces of fixed size (except the last, which may be shorter).
    Returns a generator that yields chunks.

    :param a:
    :param chunk_size:
    :yield: Chunk of array
    """
    n = len(a)
    i = 0
    while i < n:
        j = min(i + chunk_size, n)
        yield a[i:j]
        i = j


def get_sample_indices(num_obs, sample_size):
    if sample_size > num_obs:
        sample_size = num_obs

    return random.sample(range(num_obs), sample_size)


def obs_exist(sesh, history_id, vars_id, time):
    q = sesh.query(Obs).filter(
        and_(Obs.history_id == history_id, Obs.vars_id == vars_id, Obs.time == time)
    )
    return q.count() > 0


# TODO: Individual queries here could be replaced with a single query for all
#   sample observations at once, increasing speed significantly. However, this
#   function is used only for the semi-deprecated BISECTION insert strategy, so not
#   worth rewriting now.
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


def bulk_insert_strategy(sesh, observations):
    """
    This method performs a bulk insert of observations using the PostgreSQL dialect
    INSERT ... ON CONFLICT DO IGNORE clause that allows bulk inserts with duplicates
    to proceed without raising an exception (dups are ignored; new rows are inserted).

    NOTE: This only works for PostgreSQL databases. Other dialects may support a
    similar operation, but this code does not handle those cases.

    :param sesh: SQLAlchemy database session
    :param observations: List of observations to insert
    :return: DMMetrics describing result of insertion
    """
    num_to_insert = len(observations)

    # If you try to insert no rows with pg_insert, there's an unexpected insertion.
    # Avoid that.
    if num_to_insert == 0:
        return DBMetrics(0, 0, 0)

    try:
        result = sesh.execute(
            pg_insert(Obs)
            .values(observations)
            .on_conflict_do_nothing()
            .returning(Obs.id)
        ).fetchall()
    except DBAPIError:
        # This happens only if something really unanticipated happens. Duplicate
        # rows do not trigger an exception.
        return DBMetrics(0, 0, num_to_insert)

    num_inserted = len(result)
    return DBMetrics(num_inserted, num_to_insert - num_inserted, 0)


def insert(
    sesh,
    observations,
    strategy=InsertStrategy.BULK,
    bulk_chunk_size=1000,
    sample_size=50,
):
    """
    Insert a collection of observations.

    :param sesh: SQLAlchemy database session
    :param observations: For BULK insert strategy, list of dicts containing Obs rows
        to insert. For OTHER insert strategy, list of Obs objects to insert.
    :param strategy: Insert strategy. BULK is currently fastest.
    :param bulk_chunk_size: Fixed chunk size for BULK insert strategy.
    :param sample_size: Size of sample of observations to use to test for duplicates
        for BISECTION insert strategy.
    :return: dict with information about insertions
    """

    # First ensure that all pending objects (on which observations may depend) are
    # in the database.
    sesh.commit()

    with Timer() as tmr:
        if strategy == InsertStrategy.BULK:
            log.info("Using Bulk Insert Strategy")
            dbm = DBMetrics(0, 0, 0)
            for chunk in fixed_length_chunks(observations, chunk_size=bulk_chunk_size):
                dbm += bulk_insert_strategy(sesh, chunk)
        elif strategy == InsertStrategy.BISECTION:
            # Output of align is a list of dicts. These must be converted to Obs
            # objects for the consumption of BISECTION strategy. Because the ORM
            # doesn't use the same column names as the native table, this is tedious.
            observations = [
                Obs(
                    history_id=o["history_id"],
                    time=o["obs_time"],
                    datum=o["datum"],
                    vars_id=o["vars_id"],
                )
                for o in observations
            ]
            if contains_all_duplicates(sesh, observations, sample_size):
                log.info("Using Single Insert Strategy")
                dbm = single_insert_strategy(sesh, observations)
            else:
                log.info("Using Chunk + Bisection Strategy")
                dbm = DBMetrics(0, 0, 0)
                for chunk in bisection_chunks(observations):
                    dbm += bisect_insert_strategy(sesh, chunk)
        else:
            raise ValueError(f"Insert strategy has an unrecognized value: {strategy}")

    log.info("Data insertion complete")
    return {
        "successes": dbm.successes,
        "skips": dbm.skips,
        "failures": dbm.failures,
        "insertions_per_sec": round(dbm.successes / tmr.run_time, 2),
    }
