from pycds import Station, Contact

def test_can_instantiate(session):
    print "I can haz enjun"

def test_db_has_data(session):
    q = session.query(Contact.name)
    assert set([rv[0] for rv in q.all() ]) == set(['Simon', 'Pat', 'Eric'])
    q = session.query(Station)
    assert len(q.all()) == 3
