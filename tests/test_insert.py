from datetime import datetime

import pytest
import pytz

from pycds import History, Obs
from crmprtd.insert import mass_insert_obs, split, DBMetrics


@pytest.mark.parametrize(('label', 'days', 'expected'), [
    # Each obs is for a unique time
    # All should be inserted
    ('unique', range(7), 7),
    # Create 5 observations that are exactly the same
    # Repeat insertions will fail unique contraint on history/time/variable
    ('duplicates', [0 for _ in range(5)], 1),
    # None
    ('none', [], 0)
])
def test_mass_insert_obs(test_session, label, days, expected):
    # Just pick a randon variable and history entry (doesn't matter which)
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]

    obs = [Obs(history=history, datum=2.5, variable=variable,
               time=datetime(2017, 8, 6, d, tzinfo=pytz.utc))
           for d in days]

    dbm = DBMetrics()
    mass_insert_obs(test_session, obs, dbm)

    assert dbm.successes == expected


def test_mass_insert_obs_weird(test_session):
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]

    x = Obs(history=history, datum=2.5, variable=variable,
            time=datetime(2017, 8, 6, 1, tzinfo=pytz.utc))
    y = Obs(history=history, datum=2.5, variable=variable,
            time=datetime(2017, 8, 6, 1, tzinfo=pytz.utc))

    # For some reason, without expunging the objects, *both* INSERT statements
    # seem to get issued. Are we misusing the ORM?
    test_session.expunge(x)
    test_session.expunge(y)

    dbm = DBMetrics()

    mass_insert_obs(test_session, [], dbm)
    assert dbm.successes == 0
    dbm.clear()

    mass_insert_obs(test_session, [x], dbm)
    assert dbm.successes == 1
    dbm.clear()

    mass_insert_obs(test_session, [y], dbm)
    assert dbm.successes == 0


@pytest.mark.parametrize(('tuple', 'expected_a', 'expected_b'), [
    ((), (), ()),
    ((1,), 1, ()),
    ((1, 2, 3, 4), (1, 2), (3, 4))
])
def test_split(tuple, expected_a, expected_b):
    test_a, test_b = split(tuple)
    assert test_a == expected_a
    assert test_b == expected_b