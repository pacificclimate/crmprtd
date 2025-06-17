from crmprtd.networks.ec.normalize import normalize
from io import BytesIO


def test_normalize_good_data():
    lines = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
</om:ObservationCollection>"""  # noqa
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 10
    for row in rows:
        assert row.station_id is not None
        assert row.time is not None
        assert row.variable_name is not None
        assert row.val is not None
        assert row.network_name is not None


def test_normalize_no_station_id():
    lines = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
            <element name="latitude" uom="degree" value="49.025278"/>
            <element name="longitude" uom="degree" value="-122.36"/>
            <element name="transport_canada_id" uom="unitless" value="YXX"/>
            <element name="observation_date_utc" uom="unitless" value="2016-05-28T02:00:00.000Z"/>
            <element name="observation_date_local_time" uom="unitless" value="2016-05-27T19:00:00.000 PDT"/>
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
</om:ObservationCollection>"""  # noqa
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 0


def test_normalize_bad_date():
    lines = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
          <gml:timePosition>BAD_DATE</gml:timePosition>
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
</om:ObservationCollection>"""  # noqa
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 0
