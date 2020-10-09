import timeit
import os
from datetime import datetime
from statistics import mean
from argparse import ArgumentParser
from pycds import Obs
import random


def generate_best_obs(num_obs):
    best_obs = []
    for i in range(num_obs):
        time = datetime.now()
        best_obs.append(Obs(time=time, history_id=3, vars_id=7, datum=i))
    return best_obs


def generate_worst_obs(sesh, num_obs):
    worst_obs = []
    ob = Obs(time=datetime.now(), history_id=15, vars_id=7, datum=66)
    sesh.add(ob)
    sesh.commit()

    dup_ob = Obs(
        id=ob.id,
        time=ob.time,
        history_id=ob.history_id,
        vars_id=ob.vars_id,
        datum=ob.datum,
    )

    for i in range(num_obs):
        worst_obs.append(dup_ob)
    return worst_obs


def generate_scatter_obs(sesh, num_obs, num_bad):
    scatter_obs = []
    ob = Obs(time=datetime.now(), history_id=15, vars_id=7, datum=66)
    sesh.commit()
    sesh.add(ob)
    dup_ob = Obs(
        id=ob.id,
        time=ob.time,
        history_id=ob.history_id,
        vars_id=ob.vars_id,
        datum=ob.datum,
    )

    for i in range(num_obs):
        if num_bad == (num_obs - i):
            num_bad -= 1
            scatter_obs.append(dup_ob)
            continue

        if num_bad != 0:
            if random.choice([True, False, False, False]):
                num_bad -= 1
                scatter_obs.append(dup_ob)
                continue

        time = datetime.now()
        scatter_obs.append(Obs(time=time, history_id=15, vars_id=7, datum=i))

    return scatter_obs


def generate_chunk_obs(sesh, num_obs, num_bad):
    chunk_obs = []
    ob = Obs(time=datetime.now(), history_id=15, vars_id=7, datum=66)
    sesh.commit()
    sesh.add(ob)
    dup_ob = Obs(
        id=ob.id,
        time=ob.time,
        history_id=ob.history_id,
        vars_id=ob.vars_id,
        datum=ob.datum,
    )

    start_point = random.randint(1, (num_obs - num_bad + 1))
    chunk_section = False

    for i in range(num_obs):
        if i == start_point:
            chunk_section = True

        if num_bad == 0:
            chunk_section = False

        if chunk_section:
            num_bad -= 1
            chunk_obs.append(dup_ob)
            continue

        time = datetime.now()
        chunk_obs.append(Obs(time=time, history_id=15, vars_id=7, datum=i))

    return chunk_obs


def time_test(SETUP_CODE, TEST_CODE, num_iter):
    times = timeit.repeat(setup=SETUP_CODE, stmt=TEST_CODE, repeat=num_iter, number=1)
    return times


def create_results_file(fname, type):
    section = ""
    if type == "one_by_one":
        section = "One by One"
    elif type == "chunks":
        section = "Chunks"
    elif type == "bisect_strat":
        section = "Bisect Strategy"
    else:
        return

    with open(fname, "w+") as f:
        f.write("# {}\n".format(section))


def results_to_file(results, name, num_obs, case, num_iter, chunk_size, num_bad):
    fname = "insert_test_results_{}.txt".format(name)
    r_mean = mean(results)
    r_max = max(results)
    r_min = min(results)

    # check if file exists
    if not os.path.isfile(fname):
        create_results_file(fname, name)

    with open(fname, "a") as f:
        f.write("Date: {}\n".format(datetime.now()))
        f.write("Test Parameters\n")
        f.write("\tNumber of Observations:\t{}\n".format(num_obs))
        f.write("\tType of Observations:\t{}\n".format(case))
        if case == "Scatter Case" or case == "Chunk Case":
            f.write("\tNumber of Bad Observations:\t{}\n".format(num_bad))
        f.write("\tNumber of Iterations:\t{}\n".format(num_iter))
        if name == "chunks":
            f.write("\tChunk Size:\t\t\t\t{}\n".format(chunk_size))
        f.write("Time Results\n")
        f.write("\tMean:\t{}s\n".format(round(r_mean, 1)))
        f.write("\tMax:\t{}s\n".format(round(r_max, 1)))
        f.write("\tMin:\t{}s\n\n".format(round(r_min, 1)))


def get_setup_code(connection_string, observations, bad_observations):
    # Setup for timeit
    common_portion = """
from speed_test.trial_insert import insert_with_one_by_one, \
    insert_with_chunks, insert_mass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(create_engine('%s'))
sesh = Session()
""" % (
        connection_string
    )

    best_case = (
        common_portion
        + """
from __main__ import generate_best_obs
obs = generate_best_obs(%d)
"""
        % (observations)
    )

    worst_case = (
        common_portion
        + """
from __main__ import generate_worst_obs
obs = generate_worst_obs(sesh, %d)
"""
        % (observations)
    )

    chunk_case = (
        common_portion
        + """
from __main__ import generate_chunk_obs
obs = generate_chunk_obs(sesh, %d, %d)
"""
        % (observations, bad_observations)
    )

    scatter_case = (
        common_portion
        + """
from __main__ import generate_scatter_obs
obs = generate_scatter_obs(sesh, %d, %d)
"""
        % (observations, bad_observations)
    )

    return [best_case, worst_case, chunk_case, scatter_case]


def get_test_code(chunk_size):
    one_by_one = """insert_with_one_by_one(sesh, obs)"""
    chunks = """insert_with_chunks(sesh, obs, %d)""" % (chunk_size)
    mass = """insert_mass(sesh, obs)"""

    return [one_by_one, chunks, mass]


def get_case(setup):
    if "generate_best_obs" in setup:
        return "Best Case"
    elif "generate_worst_obs" in setup:
        return "Worst Case"
    elif "generate_chunk_obs" in setup:
        return "Chunk Case"
    elif "generate_scatter_obs" in setup:
        return "Scatter Case"
    else:
        return


def get_name(test):
    if "one_by_one" in test:
        return "one_by_one"
    elif "chunks" in test:
        return "chunks"
    elif "mass" in test:
        return "bisect_strat"
    else:
        return


def run_test(num_obs, num_iter, bad_obs, chunk_size, setup_list, test_list):
    for test in test_list:
        for setup in setup_list:
            results = time_test(setup, test, num_iter)
            results_to_file(
                results,
                get_name(test),
                num_obs,
                get_case(setup),
                num_iter,
                chunk_size,
                bad_obs,
            )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-x", "--connection_string", help=("Connection string for the database")
    )
    parser.add_argument(
        "-t",
        "--iterations",
        default=10,
        help="Number of times the testing code will be run",
    )
    parser.add_argument(
        "-o",
        "--observations",
        default=30000,
        help="Number of observations to be inserted",
    )
    parser.add_argument(
        "-b",
        "--bad_observations",
        default=4000,
        help="Number of bad observations to include",
    )
    parser.add_argument(
        "-c",
        "--chunk_size",
        default=4096,
        help="Size of the chunks for the chunk insertion " "strategy",
    )
    args = parser.parse_args()

    setup_list = get_setup_code(
        args.connection_string, int(args.observations), int(args.bad_observations)
    )
    test_list = get_test_code(int(args.chunk_size))

    run_test(
        int(args.observations),
        int(args.iterations),
        int(args.bad_observations),
        int(args.chunk_size),
        setup_list,
        test_list,
    )
