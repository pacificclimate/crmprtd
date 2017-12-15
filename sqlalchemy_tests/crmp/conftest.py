import pytest

import sqlalchemy.event
from sqlalchemy.schema import DDL, CreateSchema

import pycds
from pycds import Network, Station, History, Variable, Obs


@pytest.fixture(scope='function')
def create_test_database():
    def create(engine):
        engine.execute("create extension postgis")
        engine.execute(CreateSchema('crmp'))

        # Add needed functions
        sqlalchemy.event.listen(
            pycds.Base.metadata,
            'before_create',
            DDL('''CREATE OR REPLACE FUNCTION closest_stns_within_threshold(X numeric, Y numeric, thres integer)
RETURNS TABLE(history_id integer, lat numeric, lon numeric, dist double precision) AS
$BODY$

DECLARE
    mystr TEXT;
BEGIN
    mystr = 'WITH stns_in_thresh AS (
    SELECT history_id, lat, lon, Geography(ST_Transform(the_geom,4326)) as p_existing, Geography(ST_SetSRID(ST_MakePoint('|| X ||','|| Y ||'),4326)) as p_new
    FROM crmp.meta_history
    WHERE the_geom && ST_Buffer(Geography(ST_SetSRID(ST_MakePoint('|| X || ','|| Y ||'),4326)),'|| thres ||')
)
SELECT history_id, lat, lon, ST_Distance(p_existing,p_new) as dist
FROM stns_in_thresh
ORDER BY dist';
    RETURN QUERY EXECUTE mystr;
END;
$BODY$
LANGUAGE plpgsql
SECURITY DEFINER;''')
        )
        pycds.Base.metadata.create_all(bind=engine)
        pycds.DeferredBase.metadata.create_all(bind=engine)

    yield create


@pytest.fixture
def moti():
    return Network(name='MoTIe')


@pytest.fixture
def brandy_hist():
    return History(station_name='Brandywine')


@pytest.fixture
def brandy_stn(moti, brandy_hist):
    return Station(native_id='11091', network=moti, histories=[brandy_hist])


@pytest.fixture
def moti_air_temp(moti):
    return Variable(name='CURRENT_AIR_TEMPERATURE1', unit='celsius', network=moti)


@pytest.fixture
def test_session_with_moti_brandywine(
        test_session, moti, brandy_hist, brandy_stn, moti_air_temp
):
    test_session.add_all([moti, brandy_hist, brandy_stn, moti_air_temp])
    yield test_session