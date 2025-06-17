from datetime import datetime
from io import StringIO
import sys

import logging
import logging.config

import pytest
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import sessionmaker, Session
from lxml.etree import parse, fromstring, XSLT
import testing.postgresql
import pytz
import csv
import requests

import pycds
from pycds import Network, Station, Contact, History, Variable, Obs
from .swob_data import network_listing, day_listing, station_listing
from tests.test_helpers import resource_filename


def pytest_runtest_setup():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


@pytest.fixture(scope="function")
def postgis_engine():
    """
    Yields a blank PostGIS-enabled engine with a fresh db
    """
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

    with testing.postgresql.Postgresql() as pg:
        engine = sqlalchemy.create_engine(pg.url(), future=True)

        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION postgis"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
            conn.execute(CreateSchema("crmp"))
            conn.execute(text("SET search_path TO crmp,public"))

        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        yield engine


@pytest.fixture(scope="function")
def postgis_session(postgis_engine):
    """
    Yields a clean SQLAlchemy 2.x Session bound to a PostGIS engine
    """
    SessionLocal = sessionmaker(
        bind=postgis_engine, class_=Session, expire_on_commit=False, future=True
    )

    with SessionLocal() as session:
        session.execute(text("SET search_path TO crmp,public"))
        yield session


@pytest.fixture(scope="function")
def crmp_session(postgis_engine, postgis_session):
    """
    Yields a Session with CRMP schema set up but no data
    """
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

    pycds.Base.metadata.create_all(bind=postgis_engine)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    yield postgis_session


@pytest.fixture(scope="function")
def test_session(crmp_session, caplog):
    """
    Yields a PostGIS enabled session with CRMP schema and test data
    """
    caplog.set_level(logging.ERROR, logger="sqlalchemy.engine")

    moti = Network(name="MoTIe")
    ec = Network(name="EC_raw")
    wmb = Network(name="FLNRO-WMB")
    wamr = Network(name="ENV-AQN")
    crmp_session.add_all([moti, ec, wmb, wamr])

    simon = Contact(name="Simon", networks=[moti])
    eric = Contact(name="Eric", networks=[wmb])
    pat = Contact(name="Pat", networks=[ec])
    crmp_session.add_all([simon, eric, pat])

    brandy_hist = History(station_name="Brandywine")
    five_mile_hist = History(station_name="FIVE MILE")
    beaver_air_hist = History(
        id=12345,
        station_name="Beaver Creek Airport",
        the_geom=("SRID=4326;POINT(-140.866667 " "62.416667)"),
    )
    stewart_air_hist = History(
        id=10,
        station_name="Stewart Airport",
        the_geom=("SRID=4326;POINT(-129.985 " "55.9361111111111)"),
    )
    sechelt1 = History(
        id=20,
        station_name="Sechelt",
        sdate="2012-09-24",
        edate="2012-09-26",
        the_geom="SRID=4326;POINT(-123.7 49.45)",
    )
    sechelt2 = History(
        id=21,
        station_name="Sechelt",
        sdate="2012-09-26",
        the_geom=("SRID=4326;POINT(-123.7152625 " "49.4579966666667)"),
    )
    warfield = History(station_name="Warfield Elementary", sdate="2005-01-12")
    arkham = History(station_name="Arkham Asylum")

    stations = [
        Station(native_id="11091", network=moti, histories=[brandy_hist]),
        Station(native_id="1029", network=wmb, histories=[five_mile_hist, arkham]),
        Station(native_id="2100160", network=ec, histories=[beaver_air_hist]),
        Station(native_id="1067742", network=ec, histories=[stewart_air_hist]),
        Station(native_id="1047172", network=ec, histories=[sechelt1, sechelt2]),
        Station(native_id="0260011", network=wamr, histories=[warfield]),
    ]
    crmp_session.add_all(stations)

    moti_air_temp = Variable(
        name="CURRENT_AIR_TEMPERATURE1",
        standard_name="CURRENT_AIR_TEMPERATURE1",
        display_name="CURRENT_AIR_TEMPERATURE1",
        unit="celsius",
        cell_method="placeholder",
        network=moti,
    )
    ec_precip = Variable(
        name="precipitation",
        standard_name="precipitation",
        display_name="precipitation",
        unit="mm",
        cell_method="placeholder",
        network=ec,
    )
    wmb_humitidy = Variable(
        name="relative_humidity",
        standard_name="relative_humidity",
        display_name="relative_humidity",
        unit="percent",
        cell_method="placeholder",
        network=wmb,
    )
    wamr_temp = Variable(
        name="TEMP_MEAN",
        standard_name="TEMP_MEAN",
        display_name="TEMP_MEAN",
        unit="celsius",
        cell_method="placeholder",
        network=wamr,
    )
    bad_var = Variable(
        name="no_unit",
        standard_name="no_unit",
        display_name="no_unit",
        cell_method="placeholder",
        network=wamr,
    )

    crmp_session.add_all([moti_air_temp, ec_precip, wmb_humitidy, wamr_temp, bad_var])

    obs = [
        Obs(
            history=sechelt1,
            datum=2.5,
            variable=ec_precip,
            time=datetime(2012, 9, 24, 6, tzinfo=pytz.utc),
        ),
        Obs(
            history=sechelt1,
            datum=2.7,
            variable=ec_precip,
            time=datetime(2012, 9, 26, 6, tzinfo=pytz.utc),
        ),
        Obs(
            history=sechelt2,
            datum=2.5,
            variable=ec_precip,
            time=datetime(2012, 9, 26, 18, tzinfo=pytz.utc),
        ),
    ]
    crmp_session.add_all(obs)
    crmp_session.commit()

    yield crmp_session


@pytest.fixture(scope="function")
def test_data():
    lines = """station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,2018052711,.00,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052712,.00,16.4,57,9.1,152,81.667679,2.166688,5.4912086,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052713,.00,16.9,54,11.3,185,82.228363,2.5902824,6.5181026,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052714,.00,17.8,53,10.5,185,82.773972,2.6630962,6.9062028,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052715,.00,17.4,50,8.2,161,83.291313,2.5341561,6.5958676,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0
"""
    data = []
    f = StringIO(lines)
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

    return data


@pytest.fixture(scope="function")
def ec_session(crmp_session, caplog):
    """
    Yields a PostGIS enabled session with CRMP schema and test data
    """
    caplog.set_level(logging.ERROR, logger="sqlalchemy.engine")

    ec = Network(name="EC_raw")
    crmp_session.add(ec)

    pat = Contact(name="Pat", networks=[ec])
    crmp_session.add(pat)

    beaver_air_hist = History(
        id=10000,
        station_name="Beaver Creek Airport",
        the_geom=("SRID=4326;POINT(-140.866667 " "62.416667)"),
    )
    stewart_air_hist = History(
        id=10001,
        station_name="Stewart Airport",
        the_geom=("SRID=4326;POINT(-129.985 " "55.9361111111111)"),
    )
    sechelt1 = History(
        id=20000,
        station_name="Sechelt",
        freq="1-hourly",
        sdate="2012-09-24",
        edate="2012-09-26",
        the_geom="SRID=4326;POINT(-123.7 49.45)",
    )
    sechelt2 = History(
        id=20001,
        station_name="Sechelt",
        freq="1-hourly",
        sdate="2012-09-26",
        the_geom=("SRID=4326;POINT(-123.7152625 " "49.4579966666667)"),
    )

    stations = [
        Station(native_id="2100160", network=ec, histories=[beaver_air_hist]),
        Station(native_id="1067742", network=ec, histories=[stewart_air_hist]),
        Station(native_id="1047172", network=ec, histories=[sechelt1, sechelt2]),
    ]
    crmp_session.add_all(stations)

    ec_precip = Variable(
        id=100,
        name="total_precipitation",
        standard_name="total_precipitation",
        display_name="Total Precipitation",
        unit="mm",
        cell_method="placeholder",
        network=ec,
    )
    ec_precip = Variable(
        id=101,
        name="air_temperature",
        standard_name="air_temperature",
        display_name="Air Temperature",
        unit="Celsius",
        cell_method="placeholder",
        network=ec,
    )
    crmp_session.add(ec_precip)

    obs = [
        Obs(
            history=sechelt1,
            datum=2.5,
            variable=ec_precip,
            time=datetime(2012, 9, 24, 6),
        ),
        Obs(
            history=sechelt1,
            datum=2.7,
            variable=ec_precip,
            time=datetime(2012, 9, 26, 6),
        ),
        Obs(
            history=sechelt2,
            datum=2.5,
            variable=ec_precip,
            time=datetime(2012, 9, 26, 18),
        ),
    ]
    crmp_session.add_all(obs)
    crmp_session.commit()

    yield crmp_session


@pytest.fixture(scope="module")
def moti_sawr7110_xml():
    return fromstring(
        b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
  <head>
    <product operational-mode="official">
      <title>Observation from BC Meteorological Stations</title>
      <field>meteorological </field>
      <category>observation</category>
      <creation-date refresh-frequency="PT1H">2013-11-29T13:22:57-08:00</creation-date>
    </product>
    <source>
      <production-center>British Columbia Ministry of Transportation
        <sub-center>AWP</sub-center>
      </production-center>
    </source>
  </head>
  <data>
    <observation-series>
      <origin type="station">
        <id type="client">11091 </id>
        <id type="network">BC_MoT_11091 </id>
      </origin>
      <observation valid-time="2012-01-01T00:00:00-08:00">
        <pressure index="1" type="atmospheric">
          <value units="mb">964</value>
        </pressure>
        <temperature index="1" type="air-temperature">
          <value units="degC">-2.368</value>
        </temperature>
      </observation>
      <observation valid-time="2012-01-01T01:00:00-08:00">
        <temperature index="1" type="air-temperature">
          <value units="degC">-2.417</value>
        </temperature>
        <temperature index="1" type="dew-point">
          <value units="degC">-4</value>
        </temperature>
      </observation>
    </observation-series>
  </data>
</cmml>"""
    )  # noqa


@pytest.fixture(scope="module")
def moti_sawr7110_xml_2a():
    """No duplicates"""
    return fromstring(
        b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
  <head>
    <product operational-mode="official">
      <title>Observation from BC Meteorological Stations</title>
      <field>meteorological </field>
      <category>observation</category>
      <creation-date refresh-frequency="PT1H">2013-11-29T13:22:57-08:00</creation-date>
    </product>
    <source>
      <production-center>British Columbia Ministry of Transportation
        <sub-center>AWP</sub-center>
      </production-center>
    </source>
  </head>
  <data>
    <observation-series>
      <origin type="station">
        <id type="client">11091 </id>
        <id type="network">BC_MoT_11091 </id>
      </origin>
      <observation valid-time="2012-01-02T01:00:00-08:00">
        <temperature index="1" type="air-temperature">
          <value units="degC">2</value>
        </temperature>
      </observation>
    </observation-series>
  </data>
</cmml>"""
    )  # noqa


@pytest.fixture(scope="module")
def moti_sawr7110_xml_2b():
    """Duplicates observations in 2a, plus non-duplicate observations
    before and after the duplicates."""
    return fromstring(
        b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
  <head>
    <product operational-mode="official">
      <title>Observation from BC Meteorological Stations</title>
      <field>meteorological </field>
      <category>observation</category>
      <creation-date refresh-frequency="PT1H">2013-11-29T13:22:57-08:00</creation-date>
    </product>
    <source>
      <production-center>British Columbia Ministry of Transportation
        <sub-center>AWP</sub-center>
      </production-center>
    </source>
  </head>
  <data>
    <observation-series>
      <origin type="station">
        <id type="client">11091 </id>
        <id type="network">BC_MoT_11091 </id>
      </origin>
      <observation valid-time="2012-01-01T01:00:00-08:00">
        <temperature index="1" type="air-temperature">
          <value units="degC">1</value>
        </temperature>
      </observation>
      <observation valid-time="2012-01-02T01:00:00-08:00">
        <temperature index="1" type="air-temperature">
          <value units="degC">2</value>
        </temperature>
      </observation>
      <observation valid-time="2012-01-03T01:00:00-08:00">
        <temperature index="1" type="air-temperature">
          <value units="degC">3</value>
        </temperature>
      </observation>
    </observation-series>
  </data>
</cmml>"""
    )  # noqa


@pytest.fixture(scope="module")
def moti_sawr7110_new_station():
    return fromstring(
        b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
  <data>
    <observation-series>
      <origin type="station">
        <id type="client">11092</id>
      </origin>
    </observation-series>
  </data>
</cmml>"""
    )  # noqa


@pytest.fixture(scope="module")
def moti_sawr7100_large():
    return fromstring(
        b"""<?xml version="1.0" encoding="ISO-8859-1"?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
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
"""
    )  # noqa


@pytest.fixture(scope="module")
def ec_xml_single_obs():
    x = fromstring(
        b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>"""
    )  # noqa
    xsl = resource_filename("crmprtd", "data/ec_xform.xsl")
    transform = XSLT(parse(xsl))
    return transform(x)


@pytest.fixture(scope="function")
def swob_urls(requests_mock):
    def make_404(request):
        resp = requests.Response()
        resp.status_code = 404
        return resp

    requests_mock.add_matcher(make_404)
    requests_mock.register_uri(
        "GET",
        "https://dd.weather.gc.ca/observations/swob-ml/partners/bc-env-snow/",
        text=network_listing,
        status_code=200,
    )
    requests_mock.register_uri(
        "GET",
        "https://dd.weather.gc.ca/observations/swob-ml/partners/bc-env-snow/"
        "20191015/",
        text=day_listing,
        status_code=200,
    )
    requests_mock.register_uri(
        "GET",
        "https://dd.weather.gc.ca/observations/swob-ml/partners/bc-env-snow/"
        "20191015/1d06p/",
        text=station_listing,
        status_code=200,
    )
