from pkg_resources import resource_filename
from datetime import datetime
from lxml.etree import LxmlError

from io import BytesIO
from lxml.etree import fromstring, parse, XSLT
import pytest

from crmprtd.ec import makeurl, extract_fname_from_url, ns, \
    ObsProcessor, check_history, insert_obs, \
    recordable_vars, db_unit, OmMember, parse_xml
from pycds import Obs


@pytest.mark.parametrize(('label', 'args', 'expected'), [
    ('daily-BC-EN',
     {'freq': 'daily',
      'province': 'BC',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     ('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/yesterday/'
      'yesterday_bc_20160115_e.xml')
     ), ('hourly-BC-EN',
         {'freq': 'hourly',
          'province': 'BC',
          'language': 'e',
          'time': datetime(2016, 1, 15, 21)},
         ('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/'
          'hourly_bc_2016011521_e.xml')
         ), ('nofreq-BC-EN',
             {'province': 'BC',
              'language': 'e',
              'time': datetime(2016, 1, 15, 21)},
             ('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/yesterday/'
              'yesterday_bc_20160115_e.xml')
             ), ('hourly-noprov-EN',
                 {'freq': 'hourly',
                  'language': 'e',
                  'time': datetime(2016, 1, 15, 21)},
                 ('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/'
                  'hourly/hourly_bc_2016011521_e.xml')
                 ), ('hourly-BC-nolang',
                     {'freq': 'hourly',
                      'province': 'BC',
                      'time': datetime(2016, 1, 15, 21)},
                     ('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/'
                      'hourly/hourly_bc_2016011521_e.xml')
                     )
])
def test_makeurl(label, args, expected):
    assert makeurl(**args) == expected


def test_makeurl_no_time_hourly():
    url = makeurl(freq='hourly')
    fmt = '%Y%m%d%H'
    t = datetime.utcnow()

    assert url == ('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/'
                   'hourly/hourly_bc_{}_e.xml').format(t.strftime(fmt))


def test_makeurl_no_time_daily():
    url = makeurl()
    fmt = '%Y%m%d'
    t = datetime.utcnow()

    assert url == ('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/'
                   'yesterday/yesterday_bc_{}_e.xml').format(t.strftime(fmt))


@pytest.mark.parametrize(('url', 'fname'), [
    (('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/'
      'hourly_bc_2016011521_e.xml'),
     'hourly_bc_2016011521_e.xml'),
    ('http://pacificclimate.org/directory/of/files.zip', 'files.zip'),
    ('http://this.com/it/a/filename.extension', 'filename.extension')
])
def test_url_to_fname(url, fname):
    assert extract_fname_from_url(url) == fname


@pytest.mark.parametrize(('x', 'expected'), [
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:result>
        <elements>
          <element name="tendency_amount" uom="kPa" value="0.12"></element>
          <element name="tendency_characteristic" uom="code" value="falling"></element>
        </elements>
      </om:result>
    </om:Observation>
  </om:member>
</om:ObservationCollection>'''), '-0.12'), # noqa
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:result>
        <elements>
          <element name="tendency_amount" uom="kPa" value="0.12"></element>
          <element name="tendency_characteristic" uom="code" value="rising"></element>
        </elements>
      </om:result>
    </om:Observation>
  </om:member>
</om:ObservationCollection>'''), '0.12') # noqa
])
def test_xsl_transform_tendency_amount(x, expected):
    # Apply the transform
    xsl = resource_filename('crmprtd', 'data/ec_xform.xsl')
    transform = XSLT(parse(xsl))
    et = transform(x)

    # Locate changed element
    e = et.xpath(".//mpo:element", namespaces=ns)

    assert len(e) == 1
    assert e[0].attrib['value'] == expected


@pytest.mark.parametrize(('x', 'expected'), [
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:result>
        <elements>
          <element name="wind_direction" uom="code" value="W"/>
        </elements>
      </om:result>
    </om:Observation>
  </om:member>
</om:ObservationCollection>'''), '270'), # noqa
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:result>
        <elements>
          <element name="wind_direction" uom="code" value="SE"/>
        </elements>
      </om:result>
    </om:Observation>
  </om:member>
</om:ObservationCollection>'''), '135') # noqa
])
def test_xsl_transform_wind_direction(x, expected):
    # Apply the transform
    xsl = resource_filename('crmprtd', 'data/ec_xform.xsl')
    transform = XSLT(parse(xsl))
    et = transform(x)

    # Locate changed element
    e = et.xpath(".//mpo:element", namespaces=ns)

    assert e[0].attrib['value'] == expected


@pytest.mark.parametrize(('x', 'expected'), [
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:result>
        <elements>
          <element name="total_cloud_cover" uom="code" value="8"/>
        </elements>
      </om:result>
    </om:Observation>
  </om:member>
</om:ObservationCollection>'''), '8') # noqa
])
def test_xsl_transform_cloud_cover(x, expected):
    # Apply the transform
    xsl = resource_filename('crmprtd', 'data/ec_xform.xsl')
    transform = XSLT(parse(xsl))
    et = transform(x)

    # Locate changed element
    e = et.xpath(".//mpo:element", namespaces=ns)

    assert e[0].attrib['uom'] == 'percent'
    assert e[0].attrib['value'] == expected


@pytest.mark.parametrize(('et', 'expected'), [
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:metadata>
        <set>
          <general>
            <dataset name="mscobservation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/"/>
          </general>
          <identification-elements>
            <element name="station_name" uom="unitless" value="Beaver Creek Airport"/>
            <element name="climate_station_number" uom="unitless" value="2100160"/>
          </identification-elements>
        </set>
      </om:metadata>
      <om:samplingTime>
        <gml:TimeInstant>
          <gml:timePosition>2016-05-28T02:00:00.000Z</gml:timePosition>
        </gml:TimeInstant>
      </om:samplingTime>
      <om:featureOfInterest>
        <gml:FeatureCollection>
          <gml:location>
            <gml:Point>
              <gml:pos>62.416667 -140.866667</gml:pos>
            </gml:Point>
          </gml:location>
        </gml:FeatureCollection>
      </om:featureOfInterest>
    </om:Observation>
  </om:member>
</om:ObservationCollection>'''), 10000), # noqa
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:metadata>
        <set>
          <general>
            <dataset name="mscobservation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/"/>
          </general>
          <identification-elements>
            <element name="station_name" uom="unitless" value="Stewart Airport"/>
            <element name="climate_station_number" uom="unitless" value="1067742"/>
          </identification-elements>
        </set>
      </om:metadata>
      <om:samplingTime>
        <gml:TimeInstant>
          <gml:timePosition>2016-05-28T02:00:00.000Z</gml:timePosition>
        </gml:TimeInstant>
      </om:samplingTime>
      <om:featureOfInterest>
        <gml:FeatureCollection>
          <gml:location>
            <gml:Point>
              <gml:pos>55.9361 -129.985</gml:pos>
            </gml:Point>
          </gml:location>
        </gml:FeatureCollection>
      </om:featureOfInterest>
    </om:Observation>
  </om:member>
</om:ObservationCollection>'''), 10001) # noqa
])
def test_check_valid_history_id(ec_session, et, expected):
    members = et.xpath('//om:member', namespaces=ns)
    hid = check_history(members[0], ec_session, 1000)
    assert hid == expected


@pytest.mark.parametrize(('et'), [
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:metadata>
        <set>
          <general>
            <dataset name="mscobservation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/"/>
          </general>
          <identification-elements>
            <element name="station_name" uom="unitless" value="Sechelt"/>
            <element name="climate_station_number" uom="unitless" value="1047172"/>
          </identification-elements>
        </set>
      </om:metadata>
      <om:samplingTime>
        <gml:TimeInstant>
          <gml:timePosition>2012-09-28T02:00:00.000Z</gml:timePosition>
        </gml:TimeInstant>
      </om:samplingTime>
      <om:featureOfInterest>
        <gml:FeatureCollection>
          <gml:location>
            <gml:Point>
              <gml:pos>49.45 -123.7</gml:pos>
            </gml:Point>
          </gml:location>
        </gml:FeatureCollection>
      </om:featureOfInterest>
    </om:Observation>
  </om:member>
</om:ObservationCollection>''')) # noqa
])
def test_station_movement(ec_session, et):
    members = et.xpath('//om:member', namespaces=ns)
    hid = check_history(members[0], ec_session, 1000)
    assert hid


def test_new_station(ec_session):
    stn1 = fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:member xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:Observation>
    <om:metadata>
      <set>
        <general>
          <dataset name="mscobservation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/"/>
        </general>
        <identification-elements>
          <element name="station_name" uom="unitless" value="Entrance Island"/>
          <element name="climate_station_number" uom="unitless" value="1022689"/>
        </identification-elements>
      </set>
    </om:metadata>
    <om:samplingTime>
      <gml:TimeInstant>
        <gml:timePosition>2016-05-28T02:00:00.000Z</gml:timePosition>
      </gml:TimeInstant>
    </om:samplingTime>
    <om:featureOfInterest>
      <gml:FeatureCollection>
        <gml:location>
          <gml:Point>
            <gml:pos>49.208665 -123.810556</gml:pos>
          </gml:Point>
        </gml:location>
      </gml:FeatureCollection>
    </om:featureOfInterest>
  </om:Observation>
</om:member>''') # noqa
    stn2 = fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:member xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:Observation>
    <om:metadata>
      <set>
        <general>
          <dataset name="mscobservation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/"/>
        </general>
        <identification-elements>
          <element name="station_name" uom="unitless" value="Esquimalt Harbour"/>
          <element name="climate_station_number" uom="unitless" value="1012710"/>
        </identification-elements>
      </set>
    </om:metadata>
    <om:samplingTime>
      <gml:TimeInstant>
        <gml:timePosition>2016-05-28T02:00:00.000Z</gml:timePosition>
      </gml:TimeInstant>
    </om:samplingTime>
    <om:featureOfInterest>
      <gml:FeatureCollection>
        <gml:location>
          <gml:Point>
            <gml:pos>48.431972 -123.439333</gml:pos>
          </gml:Point>
        </gml:location>
      </gml:FeatureCollection>
    </om:featureOfInterest>
  </om:Observation>
</om:member>''') # noqa

    hid1 = check_history(stn1, ec_session, 1000)
    assert hid1 == 1

    hid2 = check_history(stn2, ec_session, 1000)
    assert hid2 == 2

    hid3 = check_history(stn1, ec_session, 1000)
    assert hid3 == 1


def test_get_recordable_vars(ec_session):
    rv = recordable_vars(ec_session)
    assert rv['total_precipitation'] == 100
    assert rv['air_temperature'] == 101


@pytest.mark.parametrize(('net_var_name', 'unit'), [
    ('total_precipitation', 'mm'),
    ('air_temperature', 'Celsius')
])
def test_db_unit(ec_session, net_var_name, unit):
    dbu = db_unit(ec_session, net_var_name)
    assert dbu == unit


@pytest.mark.parametrize(('et', 'hid', 'vname', 'vid'), [
    (fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:member xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
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
          <element name="station_name" uom="unitless" value="Stewart Airport"/>
          <element name="latitude" uom="degree" value="55.933333"/>
          <element name="longitude" uom="degree" value="-129.983333"/>
          <element name="transport_canada_id" uom="unitless" value="ZST"/>
          <element name="observation_date_utc" uom="unitless" value="2016-05-28T02:00:00.000Z"/>
          <element name="observation_date_local_time" uom="unitless" value="2016-05-27T19:00:00.000 PDT"/>
          <element name="climate_station_number" uom="unitless" value="1067741"/>
          <element name="wmo_station_number" uom="unitless" value=""/>
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
            <gml:pos>55.933333 -129.983333</gml:pos>
          </gml:Point>
        </gml:location>
      </gml:FeatureCollection>
    </om:featureOfInterest>
    <om:result>
      <elements>
        <element name="present_weather" uom="code" value=""/>
        <element name="mean_sea_level" uom="kPa" value="101.4"/>
        <element name="tendency_amount" uom="kPa" value="-0.03"/>
        <element name="tendency_characteristic" uom="code" value=""/>
        <element name="horizontal_visibility" uom="km" value=""/>
        <element name="air_temperature" uom="Celsius" value="13.8"/>
        <element name="dew_point" uom="Celsius" value="7.4"/>
        <element name="relative_humidity" uom="percent" value="65"/>
        <element name="wind_speed" uom="km/h" value="16"/>
        <element name="wind_direction" uom="code" value="SSW"/>
        <element name="wind_gust_speed" uom="km/h" value="29"/>
        <element name="total_cloud_cover" uom="code" value=""/>
        <element name="wind_chill" uom="unitless" value=""/>
        <element name="humidex" uom="unitless" value=""/>
      </elements>
    </om:result>
  </om:Observation>
</om:member>'''), 10001, 'air_temperature', 101) # noqa
])
def test_insert_duplicate_obs(ec_session, et, hid, vname, vid):
    from copy import deepcopy
    om1 = OmMember(et)
    om2 = OmMember(deepcopy(et))
    count1 = ec_session.query(Obs).count()
    insert_obs(ec_session, om1, hid, vname, vid)
    count2 = ec_session.query(Obs).count()
    assert count2 == (count1 + 1)

    insert_obs(ec_session, om2, hid, vname, vid)
    count3 = ec_session.query(Obs).count()
    assert count3 == count2


def test_process_xml(ec_session, caplog):
    import logging
    caplog.set_level(logging.INFO)

    from tests.ec_data import hourly_bc_2016061115, hourly_bc_2016061116

    obs_count = ec_session.query(Obs).count()

    op = ObsProcessor(hourly_bc_2016061115, ec_session, 1000)
    op.process()
    assert ec_session.query(Obs).count() == obs_count + 130

    op = ObsProcessor(hourly_bc_2016061116, ec_session, 1000)
    op.process()
    assert ec_session.query(Obs).count() == obs_count + 260


def test_parse_xml():
    et = b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:metadata>
        <set>
          <general>
            <dataset name="mscobservation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/"/>
          </general>
          <identification-elements>
            <element name="station_name" uom="unitless" value="Sechelt"/>
            <element name="climate_station_number" uom="unitless" value="1047172"/>
          </identification-elements>
        </set>
      </om:metadata>
      <om:samplingTime>
        <gml:TimeInstant>
          <gml:timePosition>2012-09-28T02:00:00.000Z</gml:timePosition>
        </gml:TimeInstant>
      </om:samplingTime>
      <om:featureOfInterest>
        <gml:FeatureCollection>
          <gml:location>
            <gml:Point>
              <gml:pos>49.45 -123.7</gml:pos>
            </gml:Point>
          </gml:location>
        </gml:FeatureCollection>
      </om:featureOfInterest>
    </om:Observation>
  </om:member>
</om:ObservationCollection>''' # noqa
    transformed = parse_xml(BytesIO(et))
    for a, b in zip(et.decode("utf-8").splitlines(),
                    transformed.__str__().splitlines()):
        if '<?xml' in a:
            # special case for first line
            assert a[:18] == b[:18]
        else:
            assert a == b


def test_process_error_handle():
    et = b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <om:member>
    <om:Observation>
      <om:metadata>
        <set>
          <general>
            <dataset name="mscobservation/atmospheric/surface_weather/wxo_dd_hour_summary-1.0-ascii/"/>
          </general>
          <identification-elements>
            <element name="station_name" uom="unitless" value="Sechelt"/>
            <element name="climate_station_number" uom="unitless" value="1047172"/>
          </identification-elements>
        </set>
      </om:metadata>
      <om:samplingTime>
        <gml:TimeInstant>
          <gml:timePosition>2012-09-28T02:00:00.000Z</gml:timePosition>
        </gml:TimeInstant>
      </om:samplingTime>
      <om:featureOfInterest>
        <gml:FeatureCollection>
          <gml:location>
            <gml:Point>
              <gml:pos>49.45 -123.7</gml:pos>
            </gml:Point>
          </gml:location>
        </gml:FeatureCollection>
      </om:featureOfInterest>
    </om:Observation>
  </om:member>
</om:ObservationCollection>''' # noqa
    with pytest.raises(Exception):
        transformed = parse_xml(BytesIO(et))
        o = ObsProcessor(transformed, 'incorrect', 'values')
        o.process()


def test_OmMember_index_error_handle(ec_session):
    et = fromstring(b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:member xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml" xmlns:om="http://www.opengis.net/om/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
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
          <element name="station_name" uom="unitless" value="Stewart Airport"/>
          <element name="latitude" uom="degree" value="55.933333"/>
          <element name="longitude" uom="degree" value="-129.983333"/>
          <element name="transport_canada_id" uom="unitless" value="ZST"/>
          <element name="observation_date_utc" uom="unitless" value="2016-05-28T02:00:00.000Z"/>
          <element name="observation_date_local_time" uom="unitless" value="2016-05-27T19:00:00.000 PDT"/>
          <element name="climate_station_number" uom="unitless" value="1067741"/>
          <element name="wmo_station_number" uom="unitless" value=""/>
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
            <gml:pos>55.933333 -129.983333</gml:pos>
          </gml:Point>
        </gml:location>
      </gml:FeatureCollection>
    </om:featureOfInterest>
    <om:result>
      <elements>
        <element name="present_weather" uom="code" value=""/>
        <element name="mean_sea_level" uom="kPa" value="101.4"/>
        <element name="tendency_amount" uom="kPa" value="-0.03"/>
        <element name="tendency_characteristic" uom="code" value=""/>
        <element name="horizontal_visibility" uom="km" value=""/>
        <element name="air_temperature" uom="Celsius" value="13.8"/>
        <element name="dew_point" uom="Celsius" value="7.4"/>
        <element name="relative_humidity" uom="percent" value="65"/>
        <element name="wind_speed" uom="km/h" value="16"/>
        <element name="wind_direction" uom="code" value="SSW"/>
        <element name="wind_gust_speed" uom="km/h" value="29"/>
        <element name="total_cloud_cover" uom="code" value=""/>
        <element name="wind_chill" uom="unitless" value=""/>
        <element name="humidex" uom="unitless" value=""/>
      </elements>
    </om:result>
  </om:Observation>
</om:member>''') # noqa
    o = OmMember(et)
    with pytest.raises(LxmlError):
        o.member_unit('test')


def test_db_unit_error_handle(ec_session):
    test_val = db_unit(ec_session, 'not_a_var')
    assert test_val is None
