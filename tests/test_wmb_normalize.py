from crmprtd.wmb_dir.normalize import reader2data

def test_reader2data():
    reader = ['here are', 'some lines that', 'could be used', 'for some tests']
    data = reader2data(reader)
    assert len(data) == 4
