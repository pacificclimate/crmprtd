from math import floor
import logging
from pythonjsonlogger import jsonlogger

from sqlalchemy.exc import IntegrityError

# globals for test
insert = 0
skip = 0
error = 0


def split(tuple_):
    if len(tuple_) < 1:
        return (), ()
    elif len(tuple_) < 2:
        return (tuple_[0], ())
    else:
        i = int(floor(len(tuple_) / 2))
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
        # json logger
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)
        log.addHandler(logHandler)

    log.info("Begin mass observation insertion", extra={'num_obs': len(obs)})

    # Base cases
    if len(obs) < 1:
        return 0
    elif len(obs) == 1:
        try:
            # Create a nested SAVEPOINT context manager to rollback to in the
            # event of unique constraint errors
            log.info("New savepoimt for singe observation")
            with sesh.begin_nested():
                sesh.add(obs[0])
        except IntegrityError as e:
            log.warning("Failure, observation already exists",
                        extra={'obs': obs, 'exception': e})
            sesh.rollback()
            return 0
        else:
            log.info("Success for single observation")
            sesh.commit()
            return 1

    # The happy case: add everything at once
    else:
        try:
            with sesh.begin_nested():
                log.info("New savepoint", extra={'num_obs': len(obs)})
                sesh.add_all(obs)
        except IntegrityError:
            log.warning("Failed to insert. Splitting observations.")
            sesh.rollback()
            a, b = split(obs)
            log.info("Splitings observations into a, b",
                     extra={'a_split': a, 'b_split': b})
            a, b = mass_insert_obs(sesh, a, log), mass_insert_obs(sesh, b, log)
            combined = a + b
            log.info("Returning from split call", extra={'a_split': a,
                                                         'b_split': b,
                                                         'both': combined})
            return a + b
        else:
            log.info("Successfully inserted observations",
                     extra={'num_obs': len(obs)})
            sesh.commit()
            return len(obs)
    return 0
