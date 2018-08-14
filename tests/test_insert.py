from datetime import datetime

import pytest
import pytz

from pycds import History, Obs
from crmprtd.db_exceptions import UniquenessError
from crmprtd.insert import bisect_insert_strategy, split, DBMetrics, chunks, \
    get_sample_indices, is_unique, has_unique_obs, single_insert_obs


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
def test_bisect_insert_strategy(test_session, label, days, expected):
    # Just pick a randon variable and history entry (doesn't matter which)
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]

    obs = [Obs(history=history, datum=2.5, variable=variable,
               time=datetime(2017, 8, 6, d, tzinfo=pytz.utc))
           for d in days]

    dbm = DBMetrics()
    bisect_insert_strategy(test_session, obs, dbm)

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

    bisect_insert_strategy(test_session, [], dbm)
    assert dbm.successes == 0
    dbm.clear()

    bisect_insert_strategy(test_session, [x], dbm)
    assert dbm.successes == 1
    dbm.clear()

    bisect_insert_strategy(test_session, [y], dbm)
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


@pytest.mark.parametrize(('list_size', 'chunk_size',
                          'expected_remainder_size'), [
    (500, 100, 0),
    (1000, 333, 1),
    (667, 99, 73)
])
def test_chunks(list_size, chunk_size, expected_remainder_size):
    test_list = []
    for i in range(list_size):
        test_list.append(i)

    for chunk in chunks(test_list, chunk_size):
        if len(chunk) == chunk_size:
            assert len(chunk) == chunk_size
        else:
            assert len(chunk) == expected_remainder_size


@pytest.mark.parametrize(('num_obs', 'num_samples', 'expected'), [
    (500, 10, [0, 50, 100, 150, 200, 250, 300, 350, 400, 450]),
    (10, 100, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
])
def test_get_sample_indices(num_obs, num_samples, expected):
    sample_indices = get_sample_indices(num_obs, num_samples)
    for index in sample_indices:
        assert index in expected


def test_is_unique(test_session):
    history_id = 20
    vars_id = 2
    time = datetime(2012, 10, 10, 6, tzinfo=pytz.utc)
    assert is_unique(test_session, history_id, vars_id, time)


def test_is_unique_not_unique(test_session):
    history_id = 20
    vars_id = 2
    time = datetime(2012, 9, 24, 6, tzinfo=pytz.utc)
    assert not is_unique(test_session, history_id, vars_id, time)


def test_has_unique_obs(test_session):
    obs_list = []
    for i in range(50):
        obs_list.append(Obs(history_id=20, vars_id=2,
                            time=datetime.now(), datum=i))

    assert has_unique_obs(test_session, obs_list, 5)


def test_has_unique_obs_not_unique(test_session):
    obs_list = []
    for i in range(50):
        obs_list.append(Obs(history_id=20,
                            vars_id=2,
                            time=datetime(2012, 9, 24, 6, tzinfo=pytz.utc),
                            datum=i))

    assert not has_unique_obs(test_session, obs_list, 5)


def test_single_insert_obs(test_session):
    ob = Obs(history_id=20, vars_id=2, time=datetime.now(), datum=10)
    dbm = DBMetrics()

    single_insert_obs(test_session, ob, dbm)

    q = test_session.query(Obs)
    assert q.count() == 4


def test_single_insert_obs_not_unique(test_session):
    ob = Obs(history_id=20, vars_id=2,
             time=datetime(2012, 9, 24, 6, tzinfo=pytz.utc), datum=10)
    dbm = DBMetrics()

    with pytest.raises(UniquenessError):
        single_insert_obs(test_session, ob, dbm)
