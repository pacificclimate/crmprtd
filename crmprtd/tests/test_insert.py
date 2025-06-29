from datetime import datetime, timedelta
from math import ceil

import pytest
import pytz

from crmprtd.more_itertools import cycles
from pycds import History, Obs
from crmprtd.insert import (
    bisect_insert_strategy,
    split,
    bisection_chunks,
    get_sample_indices,
    obs_exist,
    contains_all_duplicates,
    single_insert_strategy,
    fixed_length_chunks,
    bulk_insert_strategy,
    Timer,
)


@pytest.mark.parametrize("list_length, chunk_size", [(100, 20), (101, 20)])
def test_fixed_length_chunks(list_length, chunk_size):
    chunks = list(fixed_length_chunks(list(range(list_length)), chunk_size))
    expected_num_chunks = ceil(list_length / chunk_size)
    assert len(chunks) == expected_num_chunks
    last_chunk_length = list_length % chunk_size
    assert list(map(len, chunks)) == ([chunk_size] * (expected_num_chunks - 1)) + (
        [chunk_size] if last_chunk_length == 0 else [last_chunk_length]
    )


unique_rows = 100
total_rows = 3000


@pytest.mark.parametrize("method", (bisect_insert_strategy, bulk_insert_strategy))
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
            list(cycles(unique_rows, total_rows)),
            unique_rows,
        ),
    ],
)
def test_many_insert_strategy(test_session, method, label, days, expected):
    """Test the non-single insert strategies."""
    # Just pick a random variable and history entry (doesn't matter which)
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]

    obs = [
        # Important: We are very specifically creating the Obs object here using the ids
        #  to avoid SQLAlchemy adding this object to the session as part of its
        #  cascading backref behaviour https://goo.gl/Lchhv6
        Obs(
            history_id=history.id,
            datum=2.5,
            vars_id=variable.id,
            time=datetime(2017, 8, 6, 0, tzinfo=pytz.utc) + timedelta(days=d),
        )
        for d in days
    ]

    with Timer() as tmr:
        dbm = method(test_session, obs)
    assert dbm.successes == expected
    print("insertions_per_sec", round(dbm.successes / tmr.run_time, 2))


def test_mass_insert_obs_weird(test_session):
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]

    test_session.add_all((history, variable))

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
def test_bisection_chunks(list_size, expected):
    for chunk in bisection_chunks(list(range(list_size))):
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
