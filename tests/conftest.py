from collections import namedtuple
from pkg_resources import resource_stream, resource_filename

import logging, logging.config

import yaml
import pytest
import sqlalchemy
from sqlalchemy.schema import DDL
from sqlalchemy.orm import sessionmaker
from lxml.etree import parse, fromstring, fromstring, XSLT
import testing.postgresql

import pycds
from pycds import Network, Station, Contact, History, Variable
import sys

def pytest_runtest_setup():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

@pytest.yield_fixture(scope='function')
def postgis_session():
    '''
    Yields a blank PostGIS session with no tables or data
    '''
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR) # Let's not log all the db setup stuff...

    with testing.postgresql.Postgresql() as pg:
        engine = sqlalchemy.create_engine(pg.url())
        engine.execute("create extension postgis")
        sesh = sessionmaker(bind=engine)()

        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        yield sesh

@pytest.yield_fixture(scope='function')
def crmp_session(postgis_session):
    '''
    Yields a PostGIS enabled session with CRMP schema but no data
    '''
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR) # Let's not log all the db setup stuff...

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
    FROM meta_history
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

    engine = postgis_session.get_bind()
    pycds.Base.metadata.create_all(bind=engine)
    pycds.DeferredBase.metadata.create_all(bind=engine)

    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    yield postgis_session

@pytest.yield_fixture(scope='function')
def test_session(crmp_session):
    '''
    Yields a PostGIS enabled session with CRMP schema and test data
    '''
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR) # Let's not log all the db setup stuff...

    moti = Network(name='MoTIe')
    ec = Network(name='EC')
    wmb = Network(name='FLNROW-WMB')
    crmp_session.add_all([moti, ec, wmb])

    simon = Contact(name='Simon', networks=[moti])
    eric = Contact(name='Eric', networks=[wmb])
    pat = Contact(name='Pat', networks=[ec])
    crmp_session.add_all([simon, eric, pat])

    stations = [
        Station(native_id='11091', network=moti, histories=[History(station_name='Brandywine')]),
        Station(native_id='1029', network=wmb, histories=[History(station_name='FIVE MILE')]),
        Station(native_id='2100160', network=ec, histories=[History(station_name='Beaver Creek Airport',
                                                                    the_geom='SRID=4326;POINT(-140.866667 62.416667)')])
        ]
    crmp_session.add_all(stations)

    variables = [Variable(name='CURRENT_AIR_TEMPERATURE1', unit='celsius', network=moti),
                 Variable(name='precipitation', unit='mm', network=ec),
                 Variable(name='relative_humidity', unit='percent', network=wmb)
                 ]
    crmp_session.add_all(variables)

    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    yield crmp_session

@pytest.fixture(scope='module')
def moti_sawr7110_xml():
    return fromstring('''<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <head>
    <product operational-mode="official">
      <title>Observation from BC Meteorological Stations
      </title>
      <field>meteorological
      </field>
      <category>observation
      </category>
      <creation-date refresh-frequency="PT1H">2013-11-29T13:22:57-08:00
      </creation-date>
    </product>
    <source>
      <production-center>British Columbia Ministry of Transportation
	<sub-center>AWP
	</sub-center>
      </production-center>
    </source>
  </head>
  <data>
    <observation-series>
      <origin type="station">
	<id type="client">11091
	</id>
	<id type="network">BC_MoT_11091
	</id>
      </origin>
      <observation valid-time="2012-01-01T00:00:00-08:00">
	<pressure index="1" type="atmospheric">
	  <value units="mb">964
	  </value>
	</pressure>
	<temperature index="1" type="air-temperature">
	  <value units="degC">-2.368
	  </value>
	</temperature>
      </observation>
      <observation valid-time="2012-01-01T01:00:00-08:00">
	<temperature index="1" type="air-temperature">
	  <value units="degC">-2.417
	  </value>
	</temperature>
	<temperature index="1" type="dew-point">
	  <value units="degC">-4
	  </value>
	</temperature>
      </observation>
    </observation-series>
  </data>
</cmml>''')

@pytest.fixture(scope='module')
def moti_sawr7110_new_station():
    return fromstring('''<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <data>
    <observation-series>
      <origin type="station">
	    <id type="client">11092</id>
      </origin>
    </observation-series>
  </data>
</cmml>''')

@pytest.fixture(scope='module')
def moti_sawr7100_large():
    return fromstring('''<?xml version="1.0" encoding="ISO-8859-1"?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <head>
    <product operational-mode="official">
      <title>Observation from BC Meteorological Stations</title>
      <field>meteorological</field>
      <category>observation</category>
      <creation-date refresh-frequency="PT1H">2015-09-03T22:11:04-07:00</creation-date>
    </product>
    <source>
      <production-center>British Columbia Ministry of Transportation<sub-center>AWP</sub-center></production-center>
    </source>
  </head>
  <data>
    <observation-series>
      <origin type="station">
        <id type="client">11091</id>
        <id type="network">BC_MoT_11091</id>
      </origin>
      <observation valid-time="2011-04-07T01:00:00-07:00">
        <pressure index="1" type="atmospheric">
          <value units="mb">949</value>
        </pressure>
        <wind index="1" type="average-scalar-speed-over-60minutes">
          <value units="km/h">2.422</value>
        </wind>
        <wind index="1" type="average-direction">
          <value units="deg">6.875</value>
        </wind>
        <wind index="1" type="standard-deviation-of-direction-over-60minutes">
          <value units="deg">21.01</value>
        </wind>
        <temperature index="1" type="air-temperature">
          <value units="degC">-.813</value>
        </temperature>
        <temperature index="1" type="dew-point">
          <value units="degC">-1</value>
        </temperature>
        <precipitation index="1" type="total-over-hour">
          <value units="mm">0</value>
        </precipitation>
        <pavement index="1" type="temperature">
          <qualifier units="unitless" type="lane-number">1</qualifier>
          <value units="degC">1.7</value>
        </pavement>
        <pavement index="2" type="temperature">
          <qualifier units="unitless" type="lane-number">1</qualifier>
          <value units="degC">2.6</value>
        </pavement>
        <pavement index="1" type="freeze-point">
          <qualifier units="unitless" type="lane-number">1</qualifier>
          <value units="degC">-21.1</value>
        </pavement>
        <pavement index="1" type="surface-status">
          <qualifier type="categorical-table" units="string">BC-MoT-pavement-surface-condition-code</qualifier>
          <value units="code">24</value>
        </pavement>
        <subsurface index="1" type="temperature">
          <qualifier units="unitless" type="lane-number">1</qualifier>
          <qualifier units="cm" type="sensor-depth">25</qualifier>
          <value units="degC">6.7</value>
        </subsurface>
        <humidity index="1" type="relative-humidity">
          <value units="%">98</value>
        </humidity>
        <snow index="1" type="snowfall-accumulation-rate">
          <value units="cm">-.016</value>
        </snow>
        <snow index="1" type="adjacent-snow-depth">
          <value units="cm">97.8</value>
        </snow>
        <extension index="2">
          <qualifier units="string" type="name">bcmot-precipitation-detection-ratio</qualifier>
          <value units="unitless">.079</value>
        </extension>
      </observation>
    </observation-series>
  </data>
</cmml>
''')

@pytest.fixture(scope='module')
def ec_xml_single_obs():
    x = fromstring('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:metadata>
        <set>
          <general>
            <author build="build.4063" name="MSC-DMS-PG-WXO-Summary" version="2.4"/>
            <dataset name="mscobservation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/"/>
            <phase name="product-wxo_xml-1.0/"/>
            <id xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/product-wxo_xml-1.0/20160528024500000/bc/intermediate/en"/>
            <parent xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/product-wxo_xml-1.0/20160528024500000/bc/intermediate/en"/>
          </general>
          <identification-elements>
            <element name="station_name" uom="unitless" value="Abbotsford Airport"/>
            <element name="latitude" uom="degree" value="49.025278"/>
            <element name="longitude" uom="degree" value="-122.36"/>
            <element name="transport_canada_id" uom="unitless" value="YXX"/>
            <element name="observation_date_utc" uom="unitless" value="2016-05-28T02:00:00.000Z"/>
            <element name="observation_date_local_time" uom="unitless" value="2016-05-27T19:00:00.000 PDT"/>
            <element name="climate_station_number" uom="unitless" value="1100031"/>
            <element name="wmo_station_number" uom="unitless" value="71108"/>
          </identification-elements>
        </set>
      </om:metadata>
      <om:samplingTime>
        <gml:TimeInstant>
          <gml:timePosition>2016-05-28T02:00:00.000Z</gml:timePosition>
        </gml:TimeInstant>
      </om:samplingTime>
      <om:resultTime>
        <gml:TimeInstant>
          <gml:timePosition>2016-05-28T02:00:00.000Z</gml:timePosition>
        </gml:TimeInstant>
      </om:resultTime>
      <om:procedure xlink:href="msc/observation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/product-wxo_xml-1.0/20160528024500000/bc/intermediate/en"/>
      <om:observedProperty gml:remoteSchema="/schema/point-observation/2.0.xsd"/>
      <om:featureOfInterest>
        <gml:FeatureCollection>
          <gml:location>
            <gml:Point>
              <gml:pos>49.025278 -122.36</gml:pos>
            </gml:Point>
          </gml:location>
        </gml:FeatureCollection>
      </om:featureOfInterest>
      <om:result>
        <elements>
          <element name="present_weather" uom="code" value="Mostly Cloudy"/>
          <element name="mean_sea_level" uom="kPa" value="101.9"/>
          <element name="tendency_amount" uom="kPa" value="0.12"/>
          <element name="tendency_characteristic" uom="code" value="falling"/>
          <element name="horizontal_visibility" uom="km" value="40.2"/>
          <element name="air_temperature" uom="Celsius" value="13.7"/>
          <element name="dew_point" uom="Celsius" value="5.7"/>
          <element name="relative_humidity" uom="percent" value="58"/>
          <element name="wind_speed" uom="km/h" value="18"/>
          <element name="wind_direction" uom="code" value="S"/>
          <element name="wind_gust_speed" uom="km/h" value="29"/>
          <element name="total_cloud_cover" uom="code" value="8"/>
          <element name="wind_chill" uom="unitless" value=""/>
          <element name="humidex" uom="unitless" value=""/>
        </elements>
      </om:result>
    </om:Observation>
  </om:member>
</om:ObservationCollection>''')
    xsl = resource_filename('crmprtd', 'data/ec_xform.xsl')
    transform = XSLT(parse(xsl))
    return transform(x)