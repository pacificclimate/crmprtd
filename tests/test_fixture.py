from pycds import Contact, Network

def test_can_instantiate(test_session):
    print("I can haz enjun")

def test_db_has_data(test_session):
    q = test_session.query(Contact.name)
    assert set([rv[0] for rv in q.all() ]) == set(['Simon', 'Pat', 'Eric'])
    q = test_session.query(Network.name)
    assert set([rv[0] for rv in q.all() ]) == set(['MoTIe', 'EC_raw', 'FLNRO-WMB', 'ENV-AQN'])

def test_db_has_geo(postgis_session):
    res = postgis_session.execute("SELECT ST_AsText(ST_GeomFromText('POLYGON((0 0,0 1,1 1,1 0,0 0))',4326))")
    assert res.fetchall()[0][0] == 'POLYGON((0 0,0 1,1 1,1 0,0 0))'

def test_db_has_binary(postgis_session):
    res = postgis_session.execute("SELECT ST_AsBinary(ST_GeomFromText('POLYGON((0 0,0 1,1 1,1 0,0 0))',4326))")
    print(res.fetchall()[0][0])
