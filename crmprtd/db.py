from math import floor
import logging

import psycopg2


def split(tuple_):
    if len(tuple_) < 1:
        return (), ()
    elif len(tuple_ < 2):
        return (tuple_[0], ())
    else:
        i = floor(len(tuple_) / 2)
        return (tuple_[:i], tuple_[i:])


def mass_insert_obs(sesh, obs, log=None):
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
    if not log:
        log = logging.getLogger(__name__)

    # Base cases
    if len(obs) < 1:
        pass
    elif len(obs) == 1:
        try:
            # Create a nested SAVEPOINT context manager to rollback to in the
            # event of unique constraint errors
            with sesh.begin_nested():
                sesh.add(obs[0])
        except psycopg2.IntegrityError as e:
            log.debug("Already exists: %s %s", obs, e)
        else:
            return 1

    # The happy case: add everything at once
    else:
        try:
            with sesh.begin_nested():
                sesh.add_all(obs)
        except psycopg2.IntegrityError:
            a, b = split(obs)
            return mass_insert_obs(sesh, a, log) + \
                mass_insert_obs(sesh, b, log)
        else:
            return len(obs)
    return 0
