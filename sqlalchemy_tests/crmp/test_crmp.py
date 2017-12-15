from datetime import datetime
from collections import OrderedDict

import pytest
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from pycds import Network, Station, History, Variable, Obs


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

def test_add(
        test_session_factory,
        test_session_with_moti_brandywine,
        moti_air_temp, brandy_hist,
        insert, final_commit, args, add_result,
        obs_args_name, obs_args_list,
        nested, method, commit, rollback,
):
    """
    Test the pattern in scripts/moti_infill_insert.py that fails.
    """
    print()
    keys = args(obs_args_name, nested, method, commit, rollback)
    print('Test params:', ' | '.join('{}: {}'.format(*key) for key in keys))
    print()

    sesh = test_session_with_moti_brandywine
    sesh.commit()

    # Insert some observations
    for obs_args in obs_args_list:
        obs = Obs(
            variable=moti_air_temp,
            history=brandy_hist,
            time=datetime.strptime(obs_args[0], '%Y-%m-%dT%H:%M:%S'),
            datum=obs_args[1]
        )
        insert(sesh, obs, 'time', nested=nested, method=method, commit=commit, rollback=rollback)

    final_commit(sesh)
    sesh.close()

    sesh2 = test_session_factory()
    q = sesh2.query(Obs)
    count = q.count()
    add_result(keys, count)
    # assert q.count() == len(set(obs[0] for obs in obs_args))
    sesh2.close()