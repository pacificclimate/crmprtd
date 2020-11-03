from pycds import Obs
from sqlalchemy import and_
from crmprtd.db_exceptions import UniquenessError, InsertionError
from sqlalchemy.exc import IntegrityError
from math import floor


def insert_one_by_one(sesh, o):
    # Check to see if this entry will be unique
    try:
        q = sesh.query(Obs.id).filter(
            and_(
                Obs.history_id == o.history_id,
                Obs.vars_id == o.vars_id,
                Obs.time == o.time,
            )
        )
        if q.count() > 0:
            # print("Failure, observation already exists.")
            raise UniquenessError(q.first())
    except UniquenessError as e:
        # print("Failure, observation already exists.")
        # print(e)
        raise e
    except Exception as e:
        # print("Failure, an error occured.")
        # print(e)
        raise InsertionError(
            obs_time=o.time, datum=o.datum, vars_id=o.vars_id, hid=o.history_id, e=e
        )

    # value does not exist in obs_raw, continue with insertion
    try:
        sesh.add(o)
        sesh.rollback()
        # print("Successfully inserted observation")
        return 1
    except Exception as e:
        # print("Failure, an error occured.")
        # print(e)
        raise InsertionError(
            obs_time=o.time, datum=o.datum, vars_id=o.vars_id, hid=o.history_id, e=e
        )


def split(tuple_):
    if len(tuple_) < 1:
        return (), ()
    elif len(tuple_) < 2:
        return (tuple_[0], ())
    else:
        i = int(floor(len(tuple_) / 2))
        return (tuple_[:i], tuple_[i:])


def insert_mass(sesh, os):
    # Base cases
    if len(os) < 1:
        return 0
    elif len(os) == 1:
        try:
            # Create a nested SAVEPOINT context manager to rollback to in the
            # event of unique constraint errors
            # print("New SAVEPOINT for single observation")
            with sesh.begin_nested():
                sesh.add(os[0])
        except IntegrityError as e:
            # print("Failure, observation already exists. os: {}, "
            #       "exception: {}".format(os, e))
            sesh.rollback()
            return 0
        else:
            # print("Success for single observation")
            sesh.rollback()
            return 1

    # The happy case: add everything at once
    else:
        try:
            with sesh.begin_nested():
                # print("New SAVEPOINT. num_obs:{}".format(len(os)))
                sesh.add_all(os)
        except IntegrityError:
            # print("Failed, splitting observations.")
            sesh.rollback()
            a, b = split(os)
            # print("Splitings observations into a, b.")
            a, b = insert_mass(sesh, a), insert_mass(sesh, b)
            combined = a + b
            # print("Returning from split call")
            return combined
        else:
            # print("Successfully inserted observations")
            sesh.rollback()
            return len(os)


def insert_with_one_by_one(sesh, obs):
    for ob in obs:
        try:
            insert_one_by_one(sesh, ob)
        except Exception:
            pass


def chunks(list, chunk_size):
    for i in range(0, len(list), chunk_size):
        yield list[i : i + chunk_size]


def insert_with_chunks(sesh, obs, chunk_size):
    for chunk in chunks(obs, chunk_size):
        try:
            insert_mass(sesh, chunk)
        except Exception:
            pass
