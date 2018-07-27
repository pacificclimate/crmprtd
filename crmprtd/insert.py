"""insert.py

The insert module handles the Insert phase of the crmprtd
pipeline. This phase simply consists of doing a mass insert of
observations into the database. The phase needs to handle any unique
constraint errors, and track and report on the successes and
failures. This phase needs to manage the database transactions for
speed and reliability. This phase is common to all networks.
"""

from pycds import Obs
import datetime
from crmprtd import Timer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from sqlalchemy import and_
from crmprtd.wmb_exceptions import UniquenessError, InsertionError
import statistics


def generate_perfect_obs(num_obs):
    for i in range(num_obs):
        time = datetime.datetime.now()
        yield Obs(time=time, history_id=15, vars_id=7, datum=i)


def insert_one_by_one(sesh, o):
    # Check to see if this entry will be unique
    try:
        q = sesh.query(Obs.id).filter(
            and_(Obs.history_id == o.history_id, Obs.vars_id == o.vars_id, Obs.time == o.time))
        if q.count() > 0:
            raise UniquenessError(q.first())
    except UniquenessError as e:
        log.debug(e)
        raise e
    except Exception as e:
        log.error(e)
        raise InsertionError(obs_time=d, datum=val,
                             vars_id=vars_id, hid=hid, e=e)

    # value does not exist in obs_raw, continue with insertion
    try:
        sesh.add(o)
        return
    except Exception as e:
        log.error(e)
        raise InsertionError(obs_time=o.time, datum=o.datum,
                             vars_id=o.vars_id, hid=o.history_id, e=e)


def insert_mass(sesh, os):
    # Base cases
    if len(os) < 1:
        return 0
    elif len(os) == 1:
        try:
            # Create a nested SAVEPOINT context manager to rollback to in the
            # event of unique constraint errors
            print("New SAVEPOINT for single observation")
            with sesh.begin_nested():
                sesh.add(os[0])
        except IntegrityError as e:
            print("Failure, observation already exists. os: {}, exception: {}".format(os, e))
            sesh.rollback()
            return 0
        else:
            print("Success for single observation")
            sesh.commit()
            return 1

    # The happy case: add everything at once
    else:
        try:
            with sesh.begin_nested():
                #print("New SAVEPOINT. num_obs:{}".format(len(os)))
                sesh.add_all(os)
        except IntegrityError:
            print("Failed, splitting observations.")
            sesh.rollback()
            a, b = split(os)
            print("Splitings observations into a, b.")
            a, b = insert_with_buffer(sesh, a), insert_with_buffer(sesh, b)
            combined = a + b
            print("Returning from split call")
            return a + b
        else:
            print("Successfully inserted observations")
            sesh.commit()
            return len(os)


def insert_with_one_by_one(db, num_iter, num_obs):
    test_time_collection = []
    for i in range(num_iter):
        obs = generate_perfect_obs(num_obs)

        with Timer() as tmr:
            Session = sessionmaker(create_engine(db))
            sesh = Session()

            for ob in obs:
                insert_one_by_one(sesh, ob)

        test_time_collection.append(round(tmr.run_time, 3))
    return test_time_collection


def insert_with_chunks(db, num_iter, num_obs, chunk_size):
    test_time_collection = []
    for i in range(num_iter):
        obs_buffer = []
        tracker = 0
        obs = generate_perfect_obs(num_obs)

        with Timer() as tmr:
            Session = sessionmaker(create_engine(db))
            sesh = Session()

            for ob in obs:
                obs_buffer.append(ob)
                tracker += 1

                if tracker == chunk_size:
                    insert_mass(sesh, obs_buffer)
                    obs_buffer.clear()
                    tracker = 0

            # check for remainder
            if len(obs_buffer) != 0:
                insert_mass(sesh, obs_buffer)
        test_time_collection.append(round(tmr.run_time, 3))
    return test_time_collection


def print_results(test_time_collection, test_subject, num_iter, num_obs, chunk_size=None):
    print('\nTEST SUBJECT: {}'.format(test_subject))
    print('==================================')
    print('\tobs:\t{}'.format(num_obs))
    print('\titers:\t{}'.format(num_iter))
    if chunk_size:
        print('\tchunk:\t{}'.format(chunk_size))
    print('\tmean:\t{}'.format(statistics.mean(test_time_collection)))
    print('\tmedian:\t{}'.format(statistics.median(test_time_collection)))
    #print('\tmode:\t{}'.format(statistics.mode(test_time_collection)))
    print('\tmax:\t{}'.format(max(test_time_collection)))
    print('\tmin:\t{}\n'.format(min(test_time_collection)))


if __name__ == "__main__":
    db = 'postgres://nrados@localhost/nrados'
    # testing parameters
    num_iter = 10
    num_obs = 1000
    chunk_size = 100

    # run and calculate average time.
    one_by_one = insert_with_one_by_one(db, num_iter, num_obs)
    chunks = insert_with_chunks(db, num_iter, num_obs, chunk_size)
    mass = insert_with_chunks(db, num_iter, num_obs, num_obs)   # pass in chunk size equal to num obs to do everything at once

    print_results(one_by_one, 'One By One', num_iter, num_obs)
    print_results(chunks, 'Chunks', num_iter, num_obs, chunk_size)
    print_results(mass, 'Mass', num_iter, num_obs, num_obs)
