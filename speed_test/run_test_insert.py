from crmprtd.insert import insert
from speed_test.test_insert_speed import generate_best_obs, generate_worst_obs
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


if __name__ == '__main__':
    Session = sessionmaker(create_engine('postgres://nrados@localhost/nrados'))
    sesh = Session()

    # obs = generate_best_obs(10000)
    # obs = generate_worst_obs(sesh, 10000)

    time = datetime.now()
    obs = Obs(time=time, history_id=3, )

    chunk_size = 4096
    num_samples = 50

    results = insert(sesh, obs, chunk_size, num_samples)

    print(results)
