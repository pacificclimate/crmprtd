from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from crmprtd.sqlalchemy_test.moderate import History, Obs


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
            history=history,
        )
        insert(sesh, item, 'name', nested=nested, method=method, commit=commit, rollback=rollback)

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
        test_session_factory,
        history,
        obs_args_name, obs_args_list,
):
    def print_items():
        sesh2 = test_session_factory()
        q = sesh2.query(Obs)
        count = q.count()
        print()
        print(count, 'Items in database')
        for item in q.all():
            print(item.time)
        sesh2.close()

    print_items()

    session = test_session_factory()
    session.add(history)

    items = (
        Obs(
            time=datetime.strptime(obs_args[0], '%Y-%m-%dT%H:%M:%S'),
            history=history,
        )
        for obs_args in obs_args_list
    )

    for item in items:
        try:
            with session.begin_nested():
                session.merge(item)
            print("Inserted {}".format(item))
        except Exception as e:
            print("Skipped {} ({})".format(item, e.__class__.__name__))
        session.commit()
    session.close()

    print_items()
