
"""insert.py
The insert module handles the Insert phase of the crmprtd
pipeline. This phase simply consists of doing a mass insert of
observations into the database. The phase needs to handle any unique
constraint errors, and track and report on the successes and
failures. This phase needs to manage the database transactions for
speed and reliability. This phase is common to all networks.
"""


def insert(sesh, observations):
    successes, skips, failures = 0, 0, 0
    return {
        'successes': successes,
        'skips': skips,
        'failures': failures
    }
