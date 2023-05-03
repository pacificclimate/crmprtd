from datetime import datetime, timedelta
from itertools import chain

import pytest
import pytz

from pycds import History, Obs
from crmprtd.insert import (
    bisect_insert_strategy,
    split,
    chunks,
    get_sample_indices,
    obs_exist,
    contains_all_duplicates,
    contains_all_duplicates,
    single_insert_strategy,
    bulk_insert_strategy,
    Timer,
)


many_days = 1000


@pytest.mark.parametrize(
    ("label", "days", "expected"),
    [
        # Each obs is for a unique time
        # All should be inserted
        ("unique", range(7), 7),
        # Create 5 observations that are exactly the same
        # Repeat insertions will fail unique contraint on history/time/variable
        ("duplicates", [0 for _ in range(5)], 1),
        # None
        ("none", [], 0),
        (
            "many duplicates",
            chain(range(many_days), range(many_days), range(many_days)),
            many_days,
        ),
    ],
)
def test_bulk_insert_strategy(test_session, label, days, expected):
    # Just pick a random variable and history entry (doesn't matter which)
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]

    obs = [
        {
            "history_id": history.id,
            "datum": 2.5,
            "vars_id": variable.id,
            "obs_time": datetime(2017, 8, 6, 0, tzinfo=pytz.utc) + timedelta(days=d),
        }
        # Obs(
        #     history=history,
        #     datum=2.5,
        #     variable=variable,
        #     time=datetime(2017, 8, 6, d, tzinfo=pytz.utc),
        # )
        for d in days
    ]

    with Timer() as tmr:
        dbm = bulk_insert_strategy(test_session, obs)
    assert dbm.successes == expected
    print("insertions_per_sec", round(dbm.successes / tmr.run_time, 2))


@pytest.mark.parametrize(
    ("label", "days", "expected"),
    [
        # Each obs is for a unique time
        # All should be inserted
        ("unique", range(7), 7),
        # Create 5 observations that are exactly the same
        # Repeat insertions will fail unique contraint on history/time/variable
        ("duplicates", [0 for _ in range(5)], 1),
        # None
        ("none", [], 0),
        (
            "many duplicates",
            chain(range(many_days), range(many_days), range(many_days)),
            many_days,
        ),
    ],
)
def test_bisect_insert_strategy(test_session, label, days, expected):
    # Just pick a random variable and history entry (doesn't matter which)
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]

    obs = [
        Obs(
            history=history,
            datum=2.5,
            variable=variable,
            time=datetime(2017, 8, 6, 0, tzinfo=pytz.utc) + timedelta(days=d),
        )
        for d in days
    ]

    with Timer() as tmr:
        dbm = bisect_insert_strategy(test_session, obs)
    assert dbm.successes == expected
    print("insertions_per_sec", round(dbm.successes / tmr.run_time, 2))


def test_mass_insert_obs_weird(test_session):
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]

    x = Obs(
        history=history,
        datum=2.5,
        variable=variable,
        time=datetime(2017, 8, 6, 1, tzinfo=pytz.utc),
    )
    y = Obs(
        history=history,
        datum=2.5,
        variable=variable,
        time=datetime(2017, 8, 6, 1, tzinfo=pytz.utc),
    )

    # For some reason, without expunging the objects, *both* INSERT statements
    # seem to get issued. Are we misusing the ORM?
    test_session.expunge(x)
    test_session.expunge(y)

    dbm = bisect_insert_strategy(test_session, [])
    assert dbm.successes == 0

    dbm = bisect_insert_strategy(test_session, [x])
    assert dbm.successes == 1

    dbm = bisect_insert_strategy(test_session, [y])
    assert dbm.successes == 0


@pytest.mark.parametrize(
    ("tuple", "expected_a", "expected_b"),
    [((), (), ()), ((1,), 1, ()), ((1, 2, 3, 4), (1, 2), (3, 4))],
)
def test_split(tuple, expected_a, expected_b):
    test_a, test_b = split(tuple)
    assert test_a == expected_a
    assert test_b == expected_b


@pytest.mark.parametrize(
    ("list_size", "expected"),
    [(1200, [1024, 128, 32, 16]), (1201, [1024, 128, 32, 16, 1])],
)
def test_chunks(list_size, expected):
    test_list = []
    for i in range(list_size):
        test_list.append(i)

    for chunk in chunks(test_list):
        assert len(chunk) in expected


@pytest.mark.parametrize(
    ("num_obs", "num_samples", "expected"), [(500, 10, 10), (10, 500, 10)]
)
def test_get_sample_indices(num_obs, num_samples, expected):
    sample_indices = get_sample_indices(num_obs, num_samples)
    assert len(sample_indices) == expected


def test_obs_exist_not_in_db(test_session):
    history_id = 20
    vars_id = 2
    time = datetime(2012, 10, 10, 6, tzinfo=pytz.utc)
    assert not obs_exist(test_session, history_id, vars_id, time)


def test_obs_exist_in_db(test_session):
    history_id = 20
    vars_id = 2
    time = datetime(2012, 9, 24, 6, tzinfo=pytz.utc)
    assert obs_exist(test_session, history_id, vars_id, time)


def test_contains_all_duplicates_no_dup(test_session):
    obs_list = []
    for i in range(50):
        obs_list.append(Obs(history_id=20, vars_id=2, time=datetime.now(), datum=i))

    assert not contains_all_duplicates(test_session, obs_list, 5)


def test_contains_all_duplicates_all_dup(test_session):
    obs_list = []
    for i in range(50):
        obs_list.append(
            Obs(
                history_id=20,
                vars_id=2,
                time=datetime(2012, 9, 24, 6, tzinfo=pytz.utc),
                datum=i,
            )
        )

    assert contains_all_duplicates(test_session, obs_list, 5)


def test_single_insert_obs(test_session):
    ob = [Obs(history_id=20, vars_id=2, time=datetime.now(), datum=10)]
    dbm = single_insert_strategy(test_session, ob)
    assert dbm.successes == 1

    q = test_session.query(Obs)
    assert q.count() == 4


def test_single_insert_obs_not_unique(test_session):
    ob = [
        Obs(
            history_id=20,
            vars_id=2,
            time=datetime(2012, 9, 24, 6, tzinfo=pytz.utc),
            datum=10,
        )
    ]
    dbm = single_insert_strategy(test_session, ob)
    assert dbm.skips == 1
