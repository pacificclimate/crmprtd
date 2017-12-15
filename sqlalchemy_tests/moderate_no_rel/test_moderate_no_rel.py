from datetime import datetime

import pytest

from crmprtd.sqlalchemy_test.moderate_no_rel import Obs


@pytest.mark.parametrize('rollback', [
    False,
    True,
])
@pytest.mark.parametrize('commit', [
    False,
    True,
])
@pytest.mark.parametrize('method', [
    'Add',
    'Merge'
])
@pytest.mark.parametrize('nested', [
    False,
    True,
])
@pytest.mark.parametrize('obs_args_name, obs_args_list', [
    # ('A', [
    #     ('2017-01-01T00:00:00', 1.0),
    #     ('2017-01-02T00:00:00', 2.0),
    #     ('2017-01-03T00:00:00', 3.0),
    #     ('2017-01-04T00:00:00', 4.0),
    # ]),

    ('B', [
        ('2017-01-01T00:00:00', 1.0),
        ('2017-01-02T00:00:00', 2.0),
        ('2017-01-02T00:00:00', 2.1),
        ('2017-01-03T00:00:00', 3.0),
    ]),
])
def test_insert(
        test_session_factory,
        history,
        insert, final_commit, args, add_result,
        obs_args_name, obs_args_list,
        nested, method, commit, rollback,
):
    keys = args(obs_args_name, nested, method, commit, rollback)
    print('Test params:', ' | '.join('{}: {}'.format(*key) for key in keys))
    print()

    sesh = test_session_factory()
    for obs_args in obs_args_list:
        item = Obs(
            time=datetime.strptime(obs_args[0], '%Y-%m-%dT%H:%M:%S'),
            history_id=history.id,
        )
        insert(sesh, item, 'time', nested=nested, method=method, commit=commit, rollback=rollback)

    final_commit(sesh)
    sesh.close()

    sesh2 = test_session_factory()
    q = sesh2.query(Obs)
    count = q.count()
    add_result(keys, count)
    # assert count == len(set(names))
    sesh2.close()


@pytest.mark.parametrize('obs_args_name, obs_args_list', [
    # ('A', [
    #     ('2017-01-01T00:00:00', 1.0),
    #     ('2017-01-02T00:00:00', 2.0),
    #     ('2017-01-03T00:00:00', 3.0),
    #     ('2017-01-04T00:00:00', 4.0),
    # ]),

    ('B', [
        ('2017-01-01T00:00:00', 1.0),
        ('2017-01-02T00:00:00', 2.0),
        ('2017-01-02T00:00:00', 2.1),
        ('2017-01-03T00:00:00', 3.0),
    ]),
])
def test_sqlalchemy_doc(
        generic_test_sqlalchemy_doc,
        generic_item_count,
        test_session_with_history,
        history,
        obs_args_name, obs_args_list,
):

    items = (
        Obs(
            time=datetime.strptime(obs_args[0], '%Y-%m-%dT%H:%M:%S'),
            history_id=history.id,
        )
        for obs_args in obs_args_list
    )
    generic_test_sqlalchemy_doc(test_session_with_history, Obs, items)
    assert generic_item_count(Obs) == len(set(time for time, _ in obs_args_list))