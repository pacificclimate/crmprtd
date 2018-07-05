from math import floor
import logging

from sqlalchemy.exc import IntegrityError


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
            return 0
        else:
            log.debug("Success for single observation")
            sesh.commit()
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
            a, b = mass_insert_obs(sesh, a, log), mass_insert_obs(sesh, b, log)
            combined = a + b
            log.debug("Returning from split call", extra={'a_split': a,
                                                          'b_split': b,
                                                          'both': combined})
            return a + b
        else:
            log.debug("Successfully inserted observations",
                      extra={'num_obs': len(obs)})
            sesh.commit()
            return len(obs)
    return 0
