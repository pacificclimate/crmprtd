from pkg_resources import resource_filename
from datetime import datetime

import pytz
from lxml.etree import tostring, fromstring, parse, XSLT
import pytest

from crmprtd.ec import makeurl, extract_fname_from_url, parse_xml, ns, ObsProcessor, check_history, insert_obs
from pycds import History, Station

@pytest.mark.parametrize(('label', 'args','expected'), [
    ('daily-BC-EN',
     {'freq':'daily',
      'province': 'BC',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/yesterday/yesterday_bc_20160115_e.xml'
    ), ('hourly-BC-EN',
     {'freq':'hourly',
      'province': 'BC',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_2016011521_e.xml'
    ), ('nofreq-BC-EN',
     {'province': 'BC',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/yesterday/yesterday_bc_20160115_e.xml'
    ), ('hourly-noprov-EN',
     {'freq':'hourly',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_2016011521_e.xml'
    ), ('hourly-BC-nolang',
     {'freq':'hourly',
      'province': 'BC',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_2016011521_e.xml'
    )
])
def test_makeurl(label, args, expected):
    assert makeurl(**args) == expected

def test_makeurl_no_time_hourly():
    url = makeurl(freq='hourly')
    fmt = '%Y%m%d%H'
    t = datetime.utcnow()

    assert url == 'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_{}_e.xml'.format(t.strftime(fmt))

def test_makeurl_no_time_daily():
    url = makeurl()
    fmt = '%Y%m%d'
    t = datetime.utcnow()

    assert url == 'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/yesterday/yesterday_bc_{}_e.xml'.format(t.strftime(fmt))

@pytest.mark.parametrize(('url', 'fname'), [
    ('http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_2016011521_e.xml', 'hourly_bc_2016011521_e.xml'),
    ('http://pacificclimate.org/directory/of/files.zip', 'files.zip'),
    ('http://this.com/it/a/filename.extension', 'filename.extension')
])
def test_url_to_fname(url, fname):
    assert extract_fname_from_url(url) == fname

@pytest.mark.parametrize(('x', 'expected'), [
    (fromstring('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>'''), '-0.12'),
    (fromstring('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>'''), '0.12')
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
    (fromstring('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>'''), '270'),
    (fromstring('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>'''), '135')
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
    (fromstring('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>'''), '8')
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
    (fromstring('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>'''), 12345),
    (fromstring('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>'''), 10)
])
def test_check_valid_history_id(test_session, et, expected):
    members = et.xpath('//om:member', namespaces=ns)
    print members
    hid = check_history(members[0], test_session, 1000)
    assert hid == expected
