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
    print res.fetchall()[0][0]
    res = session.execute('''SELECT meta_history.history_id AS meta_history_history_id, 
meta_history.elev AS meta_history_elev, ST_AsBinary(meta_history.the_geom) AS meta_history_the_geom, 
meta_history.station_id AS meta_history_station_id, meta_history.station_name AS meta_history_station_name, 
meta_history.sdate AS meta_history_sdate, meta_history.edate AS meta_history_edate, 
meta_history.province AS meta_history_province, meta_history.country AS meta_history_country, 
meta_history.freq AS meta_history_freq \n
FROM meta_history JOIN meta_station ON meta_station.station_id = meta_history.station_id 
JOIN meta_network ON meta_network.network_id = meta_station.network_id \n
WHERE meta_station.native_id = '11091' AND meta_network.network_name = 'MoTIe' \n LIMIT 1''')
    print res.fetchall()[0][0]
