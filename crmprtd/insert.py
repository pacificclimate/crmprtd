
"""insert.py
The insert module handles the Insert phase of the crmprtd
pipeline. This phase simply consists of doing a mass insert of
observations into the database. The phase needs to handle any unique
constraint errors, and track and report on the successes and
failures. This phase needs to manage the database transactions for
speed and reliability. This phase is common to all networks.
"""

from math import floor, log
from sqlalchemy import and_
import logging
import time
from sqlalchemy.exc import IntegrityError

from crmprtd.db_exceptions import UniquenessError, InsertionError
from pycds import Obs


log = logging.getLogger('crmprtd.insert')


class DBMetrics(object):
    '''Keep track of database metrics during the insertion process.
    '''

    def __init__(self):
        self.successes = 0
        self.failures = 0

    def clear(self):
        self.successes = 0
        self.failures = 0


class Timer(object):
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.run_time = self.end - self.start


def pow_two_chunk(num):
    return 2 ** floor(log(num, 2))


def get_chunk_sizes(remainder):
    chunk_list = []
    while remainder != 0:
        chunk_size = pow_to_chunk(remainder)
        remainder -= chunk_size
        chunk_list.append(chunk_size)
    return chunk_list


def chunks(obs):
    pos = 0
    for chunk_size in get_chunk_sizes(len(obs))
        yield obs[pos:pos+chunk_size]
        pos += chunk_size


def get_sample_indices(num_obs, sample_size):
    if sample_size > num_obs:
        sample_size = num_obs

    return random.sample(range(num_obs), sample_size)


def ob_exists(sesh, history_id, vars_id, time):
    q = sesh.query(Obs.id).filter(
        and_(Obs.history_id == history_id, Obs.vars_id == vars_id,
             Obs.time == time))
    if q.count() > 0:
        return True
    else:
        return False


def contains_all_duplicates(sesh, observations, sample_size):
    sample_obs = []
    sample_indices = get_sample_indices(len(observations), sample_size)

    for index in sample_indices:
        sample_obs.append(observations[index])

    for sample in sample_obs:
        if not obs_exist(sesh, sample.history_id, sample.vars_id, sample.time):
            return False

    return True


def single_insert_obs(sesh, o, dbm):
    # Check to see if this entry will be unique
    if not obs_exist(sesh, o.history_id, o.vars_id, o.time):
        dbm.failures += 1
        raise UniquenessError(o)

    # value does not exist in obs_raw, continue with insertion
    try:
        sesh.add(o)
        sesh.commit()
        log.debug("Successfully inserted observation")
        dbm.successes += 1
        return 1
    except Exception as e:
        log.warning("Failure, an error occured.", extra={'e': e})
        dbm.failures += 1
        raise InsertionError(obs_time=o.time, datum=o.datum,
                             vars_id=o.vars_id, hid=o.history_id, e=e)


def split(tuple_):
    if len(tuple_) < 1:
        return (), ()
    elif len(tuple_) < 2:
        return (tuple_[0], ())
    else:
        i = int(floor(len(tuple_) / 2))
        return (tuple_[:i], tuple_[i:])


def bisect_insert_strategy(sesh, obs, dbm):
    '''This function implements a recursive Obs insert strategy to
       handle unique constraint errors on members of the set. The
       strategy used is to optimistically attempt to insert the entire
       set and in the event of a unique constraint error, it will
       divide the set into two and try again on each set (which will
       presumably have a lower probability of failing).

       In the degenerative case (all observations are duplicates), this
       strategy will require up to n *additional* transactions,
       but in the optimal case it reduces the transactions to a constant
       1.
    '''
    log.info("Begin mass observation insertion", extra={'num_obs': len(obs)})

    # Base cases
    if len(obs) < 1:
        return 0
    elif len(obs) == 1:
        try:
            # Create a nested SAVEPOINT context manager to rollback to in the
            # event of unique constraint errors
            log.debug("New SAVEPOINT for single observation")
            with sesh.begin_nested():
                sesh.add(obs[0])
        except IntegrityError as e:
            log.warning("Failure, observation already exists",
                        extra={'obs': obs, 'exception': e})
            sesh.rollback()
            dbm.failures += 1
            return 0
        else:
            log.debug("Success for single observation")
            sesh.commit()
            dbm.successes += 1
            return 1

    # The happy case: add everything at once
    else:
        try:
            with sesh.begin_nested():
                log.debug("New SAVEPOINT", extra={'num_obs': len(obs)})
                sesh.add_all(obs)
        except IntegrityError:
            log.debug("Failed, splitting observations.")
            sesh.rollback()
            a, b = split(obs)
            log.debug("Splitings observations into a, b",
                      extra={'a_split': a, 'b_split': b})
            a = bisect_insert_strategy(sesh, a, dbm)
            b = bisect_insert_strategy(sesh, b, dbm)
            combined = a + b
            log.debug("Returning from split call", extra={'a_split': a,
                                                          'b_split': b,
                                                          'both': combined})
            return combined
        else:
            log.info("Successfully inserted observations",
                     extra={'num_obs': len(obs)})
            sesh.commit()
            dbm.successes += len(obs)
            return len(obs)
    return 0


def insert(sesh, observations, chunk_size, sample_size):
    dbm = DBMetrics()

    if contains_all_duplicates(sesh, observations, sample_size):
        log.info("Using Single Insert Strategy")
        with Timer() as tmr:
            for ob in observations:
                try:
                    single_insert_obs(sesh, ob, dbm)
                except UniquenessError as e:
                    log.warning('Observation already exists in database',
                                extra={'exception': e})

    else:
        log.info("Using Chunk + Bisection Strategy")
        with Timer() as tmr:
            for chunk in chunks(observations, chunk_size):
                bisect_insert_strategy(sesh, chunk, dbm)

    log.info('Data insertion complete')
    return {'successes': dbm.successes,
            'failures': dbm.failures,
            'insertions_per_sec': (dbm.successes/tmr.run_time)}
