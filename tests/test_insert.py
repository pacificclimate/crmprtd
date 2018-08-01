import timeit
import os
from datetime import datetime
from statistics import mean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pycds import Obs


def generate_best_obs(num_obs):
    best_obs = []
    for i in range(num_obs):
        time = datetime.now()
        best_obs.append(Obs(time=time, history_id=15, vars_id=7, datum=i))
    return best_obs


def generate_worst_obs(db, num_obs):
    worst_obs = []

    # add observation that will be duplicated
    Session = sessionmaker(create_engine(db))
    sesh = Session()

    ob = Obs(time=datetime.now(), history_id=15, vars_id=7, datum=66)

    sesh.add(ob)
    sesh.commit()

    for i in range(num_obs):
        worst_obs.append(ob)
    return worst_obs


def run_time_test(SETUP_CODE, TEST_CODE, num_iter):
    times = timeit.repeat(setup = SETUP_CODE,
                          stmt = TEST_CODE,
                          repeat = num_iter,
                          number = 1)
    return times


def create_results_file(fname, type):
    section = ''
    if type == 'one_by_one':
        section = 'One by One'
    elif type == 'chunks':
        section = 'Chunks'
    elif type == 'mass':
        section = 'Mass'
    else:
        return

    with open(fname, 'w+') as f:
        f.write('# {}\n'.format(section))


def results_to_file(results, type, num_obs, obs_type, num_iter,
                    chunk_size=None):
    fname = 'insert_test_results_{}.txt'.format(type)
    r_mean = mean(results)
    r_max = max(results)
    r_min = min(results)

    # check if file exists
    if not os.path.isfile(fname):
        create_results_file(fname, type)

    with open(fname, 'a') as f:
        f.write('Date: {}\n'.format(datetime.now()))
        f.write('Test Parameters\n')
        f.write('\tNumber of Observations:\t{}\n'.format(num_obs))
        f.write('\tType of Observations:\t{}\n'.format(obs_type))
        f.write('\tNumber of Iterations:\t{}\n'.format(num_iter))
        if chunk_size:
            f.write('\tChunk Size:\t\t\t\t{}\n'.format(chunk_size))
        f.write('Time Results\n')
        f.write('\tMean:\t{}s\n'.format(round(r_mean, 1)))
        f.write('\tMax:\t{}s\n'.format(round(r_max, 1)))
        f.write('\tMin:\t{}s\n\n'.format(round(r_min, 1)))


if __name__ == "__main__":
    # connection string
    db = 'postgres://nrados@localhost/nrados'

    # testing parameters
    num_iter = 10
    num_obs = 30000
    chunk_size = 840

    # Setup for timeit
    SETUP_CODE_BEST = """
from __main__ import generate_best_obs
from crmprtd.insert import insert_with_one_by_one, insert_with_chunks, \
    insert_with_mass
obs = generate_best_obs(%d)
""" % (num_obs)

    SETUP_CODE_WORST = """
from __main__ import generate_worst_obs
from crmprtd.insert import insert_with_one_by_one, insert_with_chunks, \
    insert_with_mass
obs = generate_worst_obs('%s', %d)
""" % (db, num_obs)

    # Test code for timeit
    TEST_CODE_ONE_BY_ONE = """insert_with_one_by_one('%s', obs)""" % (db)
    TEST_CODE_CHUNKS = """insert_with_chunks('%s', obs, %d)""" % (db, chunk_size)
    TEST_CODE_MASS = """insert_with_mass('%s', obs)""" % (db)

    # One by One with best case observations
    results = run_time_test(SETUP_CODE_BEST, TEST_CODE_ONE_BY_ONE, num_iter)
    results_to_file(results, 'one_by_one', num_obs, 'Best case', num_iter)

    # One by One with worst case observations
    results = run_time_test(SETUP_CODE_WORST, TEST_CODE_ONE_BY_ONE, num_iter)
    results_to_file(results, 'one_by_one', num_obs, 'Worst Case', num_iter)

    # Chunks with best case observations
    results = run_time_test(SETUP_CODE_BEST, TEST_CODE_CHUNKS, num_iter)
    results_to_file(results, 'chunks', num_obs, 'Best Case', num_iter, chunk_size)

    # Chunks with worst case observations
    results = run_time_test(SETUP_CODE_WORST, TEST_CODE_CHUNKS, num_iter)
    results_to_file(results, 'chunks', num_obs, 'Worst Case', num_iter, chunk_size)

    # Mass with best case observations
    results = run_time_test(SETUP_CODE_BEST, TEST_CODE_MASS, num_iter)
    results_to_file(results, 'mass', num_obs, 'Best Case', num_iter)

    # Mass with worst case observations
    results = run_time_test(SETUP_CODE_WORST, TEST_CODE_MASS, num_iter)
    results_to_file(results, 'mass', num_obs, 'Worst Case', num_iter)
