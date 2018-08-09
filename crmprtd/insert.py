
"""insert.py
The insert module handles the Insert phase of the crmprtd
pipeline. This phase simply consists of doing a mass insert of
observations into the database. The phase needs to handle any unique
constraint errors, and track and report on the successes and
failures. This phase needs to manage the database transactions for
speed and reliability. This phase is common to all networks.
"""

from crmprtd.db import mass_insert_obs


def chunks(list, chunk_size):
    for i in range(0, len(list), chunk_size):
        yield list[i:i+chunk_size]


def insert(sesh, observations, chunk_size):
    dbm = DBMetrics()

    for chunk in chunks(obs, chunk_size):
        try:
            mass_insert_obs(sesh, chunk)
        except Exception:
            pass

    return {'successes': dbm.successes,
            'failures': dbm.failures,
            'skips': dbm.skips}


class DBMetrics(Object):
    '''Keep track of database successes and failures during
    the insertion process.
    '''

    def __init__(self):
        self.successes = 0
        self.failures = 0
        self.skips = 0

    def return_metrics(self):
        return self.successes, self.failures, self.skips
