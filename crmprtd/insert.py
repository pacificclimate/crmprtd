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


def generate_obs(num_obs):
    for i in range(num_obs):
        time = datetime.datetime.now()
        yield Obs(time=time, history_id=15, vars_id=7, datum=i)


def insert_with_buffer(sesh, os):
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
                print("New SAVEPOINT. num_obs:{}".format(len(os)))
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


if __name__ == "__main__":
    print('insertion test script')
    obs = generate_obs(27000)

    engine = create_engine(sys.argv[1])
    Session = sessionmaker(engine)
    sesh = Session()

    with Timer() as tmr:
        obs_buffer = []
        buff_size = 1000
        tracker = 0
        for ob in obs:
            obs_buffer.append(ob)
            tracker += 1

            if tracker == buff_size:
                insert_with_buffer(sesh, obs_buffer)
                obs_buffer.clear()
                tracker = 0

        # insert any remaining
        if len(obs_buffer) != 0:
            insert_with_buffer(sesh, obs_buffer)

    # print time
    print("Total time {}".format(tmr.run_time))
