from crmprtd.networks.ec.normalize import normalize
from io import BytesIO

# this is a partial daily summary from the Environment Canada data service
# it should result in approx 24 rows of non-empty values
partial_daily = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<om:ObservationCollection xmlns:om="http://www.opengis.net/om/1.0"
    xmlns="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml"
    xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <om:member>
        <om:Observation>
            <om:metadata>
                <set>
                    <general>
                        <author build="build.16" name="MSC-DMS-PG-WXO-Summary" version="5.1" />
                        <dataset
                            name="mscobservation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/" />
                        <phase name="product-wxo_xml-1.0/" />
                        <id
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                        <parent
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                    </general>
                    <identification-elements>
                        <element name="province" uom="unitless" value="BC" />
                        <element name="creation_date_utc" uom="unitless" value="20250701235000" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="license" uom="unitless"
                            value="https://dd.weather.gc.ca/doc/LICENCE_GENERAL.txt" />
                        <element name="language" uom="unitless" value="EN" />
                    </identification-elements>
                </set>
            </om:metadata>
            <om:samplingTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:samplingTime>
            <om:resultTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:resultTime>
            <om:procedure
                xlink:href="msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
            <om:observedProperty gml:remoteSchema="/schema/point-observation/2.0.xsd" />
            <om:featureOfInterest>
                <gml:FeatureCollection>
                    <gml:location>
                        <gml:Point>
                            <gml:pos />
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="hot_spot_location_canada" uom="unitless" value="Lytton Climate">
                        <qualifier name="hot_spot_temperature_canada" uom="Celsius" value="36.9" />
                        <qualifier name="province" uom="BC" value="unitless" />
                    </element>
                    <element name="cold_spot_location_canada" uom="unitless" value="Alert">
                        <qualifier name="cold_spot_temperature_canada" uom="Celsius" value="-3.2" />
                        <qualifier name="province" uom="NU" value="unitless" />
                    </element>
                    <element name="hot_spot_location_province" uom="unitless" value="Lytton Climate">
                        <qualifier name="hot_spot_temperature_province" uom="Celsius" value="36.9" />
                    </element>
                    <element name="cold_spot_location_province" uom="unitless"
                        value="Yoho National Park">
                        <qualifier name="cold_spot_temperature_province" uom="Celsius" value="2.9" />
                    </element>
                </elements>
            </om:result>
        </om:Observation>
    </om:member>
    <om:member>
        <om:Observation>
            <om:metadata>
                <set>
                    <general>
                        <author build="build.16" name="MSC-DMS-PG-WXO-Summary" version="5.1" />
                        <dataset
                            name="mscobservation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/" />
                        <phase name="product-wxo_xml-1.0/" />
                        <id
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                        <parent
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                    </general>
                    <identification-elements>
                        <element name="station_name" uom="unitless" value="Abbotsford Airport" />
                        <element name="latitude" uom="degree" value="49.025278" />
                        <element name="longitude" uom="degree" value="-122.36" />
                        <element name="transport_canada_id" uom="unitless" value="YXX" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1100031" />
                        <element name="wmo_station_number" uom="unitless" value="71108" />
                    </identification-elements>
                </set>
            </om:metadata>
            <om:samplingTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:samplingTime>
            <om:resultTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:resultTime>
            <om:procedure
                xlink:href="msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
            <om:observedProperty gml:remoteSchema="/schema/point-observation/2.0.xsd" />
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
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.3" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="0.0" />
                    <element name="snow_amount" uom="cm" value="0.0" />
                    <element name="wind_gust_speed" uom="km/h" value="" />
                    <element name="wind_direction" uom="code" value="" />
                </elements>
            </om:result>
        </om:Observation>
    </om:member>
    <om:member>
        <om:Observation>
            <om:metadata>
                <set>
                    <general>
                        <author build="build.16" name="MSC-DMS-PG-WXO-Summary" version="5.1" />
                        <dataset
                            name="mscobservation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/" />
                        <phase name="product-wxo_xml-1.0/" />
                        <id
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                        <parent
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                    </general>
                    <identification-elements>
                        <element name="station_name" uom="unitless" value="Agassiz" />
                        <element name="latitude" uom="degree" value="49.243056" />
                        <element name="longitude" uom="degree" value="-121.760278" />
                        <element name="transport_canada_id" uom="unitless" value="WZA" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1100119" />
                        <element name="wmo_station_number" uom="unitless" value="71113" />
                    </identification-elements>
                </set>
            </om:metadata>
            <om:samplingTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:samplingTime>
            <om:resultTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:resultTime>
            <om:procedure
                xlink:href="msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
            <om:observedProperty gml:remoteSchema="/schema/point-observation/2.0.xsd" />
            <om:featureOfInterest>
                <gml:FeatureCollection>
                    <gml:location>
                        <gml:Point>
                            <gml:pos>49.243056 -121.760278</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="30.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.8" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="" />
                    <element name="wind_direction" uom="code" value="" />
                </elements>
            </om:result>
        </om:Observation>
    </om:member>
    <om:member>
        <om:Observation>
            <om:metadata>
                <set>
                    <general>
                        <author build="build.16" name="MSC-DMS-PG-WXO-Summary" version="5.1" />
                        <dataset
                            name="mscobservation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/" />
                        <phase name="product-wxo_xml-1.0/" />
                        <id
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                        <parent
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                    </general>
                    <identification-elements>
                        <element name="station_name" uom="unitless" value="Ashcroft" />
                        <element name="latitude" uom="degree" value="50.708335" />
                        <element name="longitude" uom="degree" value="-121.281389" />
                        <element name="transport_canada_id" uom="unitless" value="VAS" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1160515" />
                        <element name="wmo_station_number" uom="unitless" value="71681" />
                    </identification-elements>
                </set>
            </om:metadata>
            <om:samplingTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:samplingTime>
            <om:resultTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:resultTime>
            <om:procedure
                xlink:href="msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
            <om:observedProperty gml:remoteSchema="/schema/point-observation/2.0.xsd" />
            <om:featureOfInterest>
                <gml:FeatureCollection>
                    <gml:location>
                        <gml:Point>
                            <gml:pos>50.708335 -121.281389</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="36.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="15.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="" />
                    <element name="wind_direction" uom="code" value="" />
                </elements>
            </om:result>
        </om:Observation>
    </om:member>
    <om:member>
        <om:Observation>
            <om:metadata>
                <set>
                    <general>
                        <author build="build.16" name="MSC-DMS-PG-WXO-Summary" version="5.1" />
                        <dataset
                            name="mscobservation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/" />
                        <phase name="product-wxo_xml-1.0/" />
                        <id
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                        <parent
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                    </general>
                    <identification-elements>
                        <element name="station_name" uom="unitless" value="Ballenas Islands" />
                        <element name="latitude" uom="degree" value="49.350278" />
                        <element name="longitude" uom="degree" value="-124.160278" />
                        <element name="transport_canada_id" uom="unitless" value="WGB" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1020590" />
                        <element name="wmo_station_number" uom="unitless" value="71769" />
                    </identification-elements>
                </set>
            </om:metadata>
            <om:samplingTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:samplingTime>
            <om:resultTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:resultTime>
            <om:procedure
                xlink:href="msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
            <om:observedProperty gml:remoteSchema="/schema/point-observation/2.0.xsd" />
            <om:featureOfInterest>
                <gml:FeatureCollection>
                    <gml:location>
                        <gml:Point>
                            <gml:pos>49.350278 -124.160278</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="24.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="17.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="43" />
                    <element name="wind_direction" uom="code" value="W" />
                </elements>
            </om:result>
        </om:Observation>
    </om:member>
    <om:member>
        <om:Observation>
            <om:metadata>
                <set>
                    <general>
                        <author build="build.16" name="MSC-DMS-PG-WXO-Summary" version="5.1" />
                        <dataset
                            name="mscobservation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/" />
                        <phase name="product-wxo_xml-1.0/" />
                        <id
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                        <parent
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                    </general>
                    <identification-elements>
                        <element name="station_name" uom="unitless" value="Bella Bella Airport" />
                        <element name="latitude" uom="degree" value="52.185" />
                        <element name="longitude" uom="degree" value="-128.156667" />
                        <element name="transport_canada_id" uom="unitless" value="BBC" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1060815" />
                        <element name="wmo_station_number" uom="unitless" value="71582" />
                    </identification-elements>
                </set>
            </om:metadata>
            <om:samplingTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:samplingTime>
            <om:resultTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:resultTime>
            <om:procedure
                xlink:href="msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
            <om:observedProperty gml:remoteSchema="/schema/point-observation/2.0.xsd" />
            <om:featureOfInterest>
                <gml:FeatureCollection>
                    <gml:location>
                        <gml:Point>
                            <gml:pos>52.185 -128.156667</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="20.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.1" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="" />
                    <element name="wind_direction" uom="code" value="" />
                </elements>
            </om:result>
        </om:Observation>
    </om:member>
    <om:member>
        <om:Observation>
            <om:metadata>
                <set>
                    <general>
                        <author build="build.16" name="MSC-DMS-PG-WXO-Summary" version="5.1" />
                        <dataset
                            name="mscobservation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/" />
                        <phase name="product-wxo_xml-1.0/" />
                        <id
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                        <parent
                            xlink:href="/data/msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
                    </general>
                    <identification-elements>
                        <element name="station_name" uom="unitless" value="Bella Coola" />
                        <element name="latitude" uom="degree" value="52.388611" />
                        <element name="longitude" uom="degree" value="-126.586944" />
                        <element name="transport_canada_id" uom="unitless" value="VBD" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1060844" />
                        <element name="wmo_station_number" uom="unitless" value="71533" />
                    </identification-elements>
                </set>
            </om:metadata>
            <om:samplingTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:samplingTime>
            <om:resultTime>
                <gml:TimeInstant>
                    <gml:timePosition>2025-07-01T23:00:00.000Z</gml:timePosition>
                </gml:TimeInstant>
            </om:resultTime>
            <om:procedure
                xlink:href="msc/observation/atmospheric/surface_weather/wxo_dd_yesterday_summary-1.0-ascii/product-wxo_xml-1.0/20250701234500000/bc/intermediate/en" />
            <om:observedProperty gml:remoteSchema="/schema/point-observation/2.0.xsd" />
            <om:featureOfInterest>
                <gml:FeatureCollection>
                    <gml:location>
                        <gml:Point>
                            <gml:pos>52.388611 -126.586944</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="46" />
                    <element name="wind_direction" uom="code" value="SW" />
                </elements>
            </om:result>
        </om:Observation>
    </om:member>
</om:ObservationCollection>
"""  # noqa


def test_normalize_good_data():
    lines = partial_daily
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 24
    for row in rows:
        assert row.station_id is not None
        assert row.time is not None
        assert row.variable_name is not None
        assert row.val is not None
        assert row.network_name is not None


variable_names = [
    "air_temperature_yesterday_high",
    "air_temperature_yesterday_low",
    # 'total_precipitation', # this is present in the configuration but doesn't currently change the value
    "wind_direction",
    "wind_gust_speed",
]


def test_variable_replace():
    lines = partial_daily
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 24
    for row in rows:
        assert row.variable_name not in variable_names


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
