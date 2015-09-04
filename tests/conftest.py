from collections import namedtuple
from pkg_resources import resource_stream
import logging, logging.config

import yaml
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lxml.etree import parse, fromstring

from pycds.util import create_test_database
from pycds import Network, Station, Contact, History, Variable
import sys

def pytest_runtest_setup():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

@pytest.fixture(scope='function')
def in_memory_crmpdb_engine():
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR) # Let's not log all the db setup stuff...
    engine = create_engine('sqlite://')
    create_test_database(engine)

    sesh = sessionmaker(bind=engine)()
    sesh.connection().connection.enable_load_extension(True)
    sesh.execute("select load_extension('libspatialite.so')")

    moti = Network(name='MoTIe')
    ec = Network(name='EC')
    wmb = Network(name='FLNROW-WMB')
    sesh.add_all([moti, ec, wmb])

    simon = Contact(name='Simon', networks=[moti])
    eric = Contact(name='Eric', networks=[wmb])
    pat = Contact(name='Pat', networks=[ec])
    sesh.add_all([simon, eric, pat])

    stations = [
        Station(native_id='11091', network=moti, histories=[History(station_name='Brandywine')]),
        Station(native_id='1029', network=wmb, histories=[History(station_name='FIVE MILE')]),
        Station(native_id='2100160', network=ec, histories=[History(station_name='Beaver Creek Airport')])
        ]
    sesh.add_all(stations)

    variables = [Variable(name='CURRENT_AIR_TEMPERATURE1', unit='celsius', network=moti),
                 Variable(name='precipitation', unit='mm', network=ec),
                 Variable(name='relative_humidity', unit='percent', network=wmb)
                 ]
    sesh.add_all(variables)

    sesh.commit()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO) # Re-enable sqlalchemy logging
    return engine

@pytest.fixture(scope='function')
def session(in_memory_crmpdb_engine):
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=in_memory_crmpdb_engine)()

# http://blog.fizyk.net.pl/blog/testing-web-applications-using-sqlalchemy.html
# TODO: make this work this is a rough first idea/draft
@pytest.fixture(scope='function', params=['sqlite', 'mysql', 'postgresql'])
def db_session(request):
    """SQLAlchemy session."""
    from pyramid_fullauth.models import Base

    if request.param == 'sqlite':
        connection = 'sqlite:///fullauth.sqlite'
    elif request.param == 'mysql':
        request.getfuncargvalue('mysqldb')  # takes care of creating database
        connection = 'mysql+mysqldb://root:@127.0.0.1:3307/tests?charset=utf8'
    elif request.param == 'postgresql':
        request.getfuncargvalue('postgresql')  # takes care of creating database
        connection = 'postgresql+psycopg2://postgres:@127.0.0.1:5433/tests'

    engine = create_engine(connection, echo=False, poolclass=NullPool)
    pyramid_basemodel.Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    pyramid_basemodel.bind_engine(engine, pyramid_basemodel.Session, should_drop=True)

    def destroy():
        transaction.commit()
        Base.metadata.drop_all(engine)

    request.addfinalizer(destroy)

    return pyramid_basemodel.Session
    
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

def moti_sawr7100_large():
    return '''<?xml version="1.0" encoding="ISO-8859-1"?>
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
'''
