from pycds import Station, Contact

def test_can_instantiate(session):
    print "I can haz enjun"

def test_db_has_data(session):
    q = session.query(Contact.name)
    assert set([rv[0] for rv in q.all() ]) == set(['Simon', 'Pat', 'Eric'])
    q = session.query(Station)
    assert len(q.all()) == 3

def test_db_has_geo(session):
    res = session.execute("SELECT ST_AsText(ST_GeomFromText('POLYGON((0 0,0 1,1 1,1 0,0 0))',4326))")
    assert res.fetchall()[0][0] == 'POLYGON((0 0,0 1,1 1,1 0,0 0))'

def test_db_has_binary(session):
    res = session.execute("SELECT ST_AsBinary(ST_GeomFromText('POLYGON((0 0,0 1,1 1,1 0,0 0))',4326))")
