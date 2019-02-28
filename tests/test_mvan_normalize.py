from pkg_resources import resource_stream

from crmprtd.mvan.normalize import normalize


def test_normalize_good_data():
    with resource_stream('crmprtd', 'data/mvan.csv') as file_stream:
        for row in normalize(file_stream):
            assert row
