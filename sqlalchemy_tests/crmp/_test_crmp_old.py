from datetime import datetime
from collections import OrderedDict

import pytest
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from pycds import Network, Station, History, Variable, Obs


def add1(sesh, observations, commit=False, rollback=False):
    successes = commits = 0
    integrity_errors = invalid_request_errors = rollbacks = 0
    for obs in observations:
        try:
            print("Inserting {}".format(obs.time))
            with sesh.begin_nested():
                sesh.merge(obs)
                # sesh.add(obs)
            if commit:
                sesh.commit()
                commits += 1
            successes += 1
        except IntegrityError as e:
            print('>> IntegrityError')
            if rollback:
                sesh.rollback()
                rollbacks += 1
            integrity_errors += 1
        except InvalidRequestError as e:
            print('>> InvalidRequestError')
            if rollback:
                sesh.rollback()
                rollbacks += 1
            invalid_request_errors += 1
    return OrderedDict([
        ('successes', successes),
        ('commits', commits),
        ('integrity_errors', integrity_errors),
        ('invalid_request_errors', invalid_request_errors),
        ('rollbacks', rollbacks),
    ])


def add2(sesh, obs_args, action='add', commit=False, rollback=False):
    successes = commits = 0
    integrity_errors = invalid_request_errors = rollbacks = 0
    for args in obs_args:
        obs = Obs(**args)
        try:
            print("Inserting {}".format(obs.time))
            with sesh.begin_nested():
                {'add': sesh.add, 'merge': sesh.merge}[action](obs)
            if commit:
                sesh.commit()
                commits += 1
            successes += 1
        except IntegrityError as e:
            print('>> IntegrityError')
            if rollback:
                sesh.rollback()
                rollbacks += 1
            integrity_errors += 1
        except InvalidRequestError as e:
            print('>> InvalidRequestError')
            if rollback:
                sesh.rollback()
                rollbacks += 1
            invalid_request_errors += 1
    return OrderedDict([
        ('successes', successes),
        ('commits', commits),
        ('integrity_errors', integrity_errors),
        ('invalid_request_errors', invalid_request_errors),
        ('rollbacks', rollbacks),
    ])


@pytest.mark.parametrize('rollback', [
    False,
    True,
], ids=['NR', 'RR'])
@pytest.mark.parametrize('commit', [
    False,
    True,
], ids=['NC', 'CC'])
@pytest.mark.parametrize('action', [
    'add',
    'merge'
])
@pytest.mark.parametrize('obs_args', [
    # [
    #     ('2017-01-01T00:00:00', 1.0),
    #     ('2017-01-02T00:00:00', 2.0),
    #     ('2017-01-03T00:00:00', 3.0),
    #     ('2017-01-04T00:00:00', 4.0),
    # ],

    [
        ('2017-01-01T00:00:00', 1.0),
        ('2017-01-02T00:00:00', 2.0),
        ('2017-01-03T00:00:00', 3.0),
        ('2017-01-03T00:00:00', 3.1),
        ('2017-01-04T00:00:00', 4.0),
    ],
])

def test_add(
        test_session_factory,
        test_session_with_moti_brandywine,
        moti_air_temp, brandy_hist,
        obs_args, action, commit, rollback
):
    """
    Test the pattern in scripts/moti_infill_insert.py that fails.
    """
    print()
    sesh = test_session_with_moti_brandywine
    sesh.commit()

    def make_obs(timestr, datum):
        return Obs(
            variable=moti_air_temp,
            history=brandy_hist,
            time=datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%S'),
            datum=datum
        )

    # Insert some observations
    # observations = [make_obs(*args) for args in obs_args]
    # results = add1(sesh, observations, commit=commit, rollback=rollback)
    obs_kwargs = [
        dict(
            variable=moti_air_temp,
            history=brandy_hist,
            time=datetime.strptime(args[0], '%Y-%m-%dT%H:%M:%S'),
            datum=args[1]
        )
        for args in obs_args
    ]
    results = add2(sesh, obs_kwargs, commit=commit, rollback=rollback)
    # for k, v in results.items():
    #     print(k, v)
    print('  ', ', '.join('{}: {}'.format(k, v) for k, v in results.items()))
    try:
        sesh.commit()
    except Exception as e:
        print('Exception during test query', e.__class__.__name__)

    sesh2 = test_session_factory()
    q = sesh2.query(Obs)
    print("{c} observations in database".format(c=q.count()))
    assert q.count() == len(set(obs[0] for obs in obs_args))
    # try:
    #     assert q.count() == len(set(obs[0] for obs in obs_args))
    # except AssertionError as e:
    #     print(e)
    sesh2.close()