from lxml.etree import fromstring

hourly_bc_2016061115 = fromstring(
    b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
                        <element name="station_name" uom="unitless" value="Blue River" />
                        <element name="latitude" uom="degree" value="52.129" />
                        <element name="longitude" uom="degree" value="-119.289917" />
                        <element name="transport_canada_id" uom="unitless" value="WSV" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1160H99" />
                        <element name="wmo_station_number" uom="unitless" value="71883" />
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
                            <gml:pos>52.129 -119.289917</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="30.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="7.9" />
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
                        <element name="station_name" uom="unitless" value="Bonilla Island" />
                        <element name="latitude" uom="degree" value="53.49285" />
                        <element name="longitude" uom="degree" value="-130.639" />
                        <element name="transport_canada_id" uom="unitless" value="WWL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1060R0K" />
                        <element name="wmo_station_number" uom="unitless" value="71484" />
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
                            <gml:pos>53.49285 -130.639</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="13.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.4" />
                    <element name="total_precipitation" uom="mm" value="2.6" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="54" />
                    <element name="wind_direction" uom="code" value="SE" />
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
                        <element name="station_name" uom="unitless" value="Burns Lake Airport" />
                        <element name="latitude" uom="degree" value="54.383167" />
                        <element name="longitude" uom="degree" value="-125.958667" />
                        <element name="transport_canada_id" uom="unitless" value="WPZ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1091174" />
                        <element name="wmo_station_number" uom="unitless" value="71952" />
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
                            <gml:pos>54.383167 -125.958667</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="23.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="5.0" />
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
                        <element name="station_name" uom="unitless" value="Callaghan Valley" />
                        <element name="latitude" uom="degree" value="50.143905" />
                        <element name="longitude" uom="degree" value="-123.110558" />
                        <element name="transport_canada_id" uom="unitless" value="VOD" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1101300" />
                        <element name="wmo_station_number" uom="unitless" value="71688" />
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
                            <gml:pos>50.143905 -123.110558</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.6" />
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
                        <element name="station_name" uom="unitless" value="Cape St.James" />
                        <element name="latitude" uom="degree" value="51.935833" />
                        <element name="longitude" uom="degree" value="-131.015833" />
                        <element name="transport_canada_id" uom="unitless" value="WZV" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1051351" />
                        <element name="wmo_station_number" uom="unitless" value="71107" />
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
                            <gml:pos>51.935833 -131.015833</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="13.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.7" />
                    <element name="total_precipitation" uom="mm" value="0.2" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="39" />
                    <element name="wind_direction" uom="code" value="S" />
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
                        <element name="station_name" uom="unitless" value="Cathedral Point" />
                        <element name="latitude" uom="degree" value="52.187453" />
                        <element name="longitude" uom="degree" value="-127.471161" />
                        <element name="transport_canada_id" uom="unitless" value="WME" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1061458" />
                        <element name="wmo_station_number" uom="unitless" value="71482" />
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
                            <gml:pos>52.187453 -127.471161</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="20.1" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.1" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="35" />
                    <element name="wind_direction" uom="code" value="SW" />
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
                        <element name="station_name" uom="unitless" value="Clearwater" />
                        <element name="latitude" uom="degree" value="51.652583" />
                        <element name="longitude" uom="degree" value="-120.082333" />
                        <element name="transport_canada_id" uom="unitless" value="VCW" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1161650" />
                        <element name="wmo_station_number" uom="unitless" value="71645" />
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
                            <gml:pos>51.652583 -120.082333</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="32.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.4" />
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
                        <element name="station_name" uom="unitless" value="Clinton" />
                        <element name="latitude" uom="degree" value="51.266389" />
                        <element name="longitude" uom="degree" value="-121.684722" />
                        <element name="transport_canada_id" uom="unitless" value="YIN" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1161662" />
                        <element name="wmo_station_number" uom="unitless" value="71717" />
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
                            <gml:pos>51.266389 -121.684722</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="27.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="5.1" />
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
                        <element name="station_name" uom="unitless" value="Comox Airport" />
                        <element name="latitude" uom="degree" value="49.716667" />
                        <element name="longitude" uom="degree" value="-124.9" />
                        <element name="transport_canada_id" uom="unitless" value="YQQ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1021830" />
                        <element name="wmo_station_number" uom="unitless" value="71893" />
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
                            <gml:pos>49.716667 -124.9</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="16.3" />
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
                        <element name="station_name" uom="unitless" value="Cranbrook Airport" />
                        <element name="latitude" uom="degree" value="49.612222" />
                        <element name="longitude" uom="degree" value="-115.781944" />
                        <element name="transport_canada_id" uom="unitless" value="YXC" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T17:45:00.000 MDT" />
                        <element name="climate_station_number" uom="unitless" value="1152105" />
                        <element name="wmo_station_number" uom="unitless" value="71880" />
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
                            <gml:pos>49.612222 -115.781944</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="30.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.1" />
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
                        <element name="station_name" uom="unitless" value="Creston" />
                        <element name="latitude" uom="degree" value="49.081689" />
                        <element name="longitude" uom="degree" value="-116.50068" />
                        <element name="transport_canada_id" uom="unitless" value="WJR" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 MST" />
                        <element name="climate_station_number" uom="unitless" value="114B1F0" />
                        <element name="wmo_station_number" uom="unitless" value="71770" />
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
                            <gml:pos>49.081689 -116.50068</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="32.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.0" />
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
                        <element name="station_name" uom="unitless" value="Cumshewa Island" />
                        <element name="latitude" uom="degree" value="53.03041" />
                        <element name="longitude" uom="degree" value="-131.601555" />
                        <element name="transport_canada_id" uom="unitless" value="WZL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1062251" />
                        <element name="wmo_station_number" uom="unitless" value="71771" />
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
                            <gml:pos>53.03041 -131.601555</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="17.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.6" />
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
                        <element name="station_name" uom="unitless" value="Dawson Creek Airport" />
                        <element name="latitude" uom="degree" value="55.742222" />
                        <element name="longitude" uom="degree" value="-120.183056" />
                        <element name="transport_canada_id" uom="unitless" value="YDQ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 MST" />
                        <element name="climate_station_number" uom="unitless" value="1182289" />
                        <element name="wmo_station_number" uom="unitless" value="71471" />
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
                            <gml:pos>55.742222 -120.183056</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.1" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="37" />
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
                        <element name="station_name" uom="unitless" value="Dease Lake Airport" />
                        <element name="latitude" uom="degree" value="58.422222" />
                        <element name="longitude" uom="degree" value="-130.031389" />
                        <element name="transport_canada_id" uom="unitless" value="YDL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1192341" />
                        <element name="wmo_station_number" uom="unitless" value="71686" />
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
                            <gml:pos>58.422222 -130.031389</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="16.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="5.7" />
                    <element name="total_precipitation" uom="mm" value="4.3" />
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
                        <element name="station_name" uom="unitless" value="Dease Lake Climate" />
                        <element name="latitude" uom="degree" value="58.4261" />
                        <element name="longitude" uom="degree" value="-130.025" />
                        <element name="transport_canada_id" uom="unitless" value="WKX" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="119BLM0" />
                        <element name="wmo_station_number" uom="unitless" value="71222" />
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
                            <gml:pos>58.4261 -130.025</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="16.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="5.7" />
                    <element name="total_precipitation" uom="mm" value="4.4" />
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
                        <element name="station_name" uom="unitless" value="Delta Burns Bog" />
                        <element name="latitude" uom="degree" value="49.125848" />
                        <element name="longitude" uom="degree" value="-123.002246" />
                        <element name="transport_canada_id" uom="unitless" value="VBB" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1102415" />
                        <element name="wmo_station_number" uom="unitless" value="71042" />
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
                            <gml:pos>49.125848 -123.002246</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.5" />
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
                        <element name="station_name" uom="unitless" value="Discovery Island" />
                        <element name="latitude" uom="degree" value="48.424608" />
                        <element name="longitude" uom="degree" value="-123.2257" />
                        <element name="transport_canada_id" uom="unitless" value="WDR" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1012475" />
                        <element name="wmo_station_number" uom="unitless" value="71031" />
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
                            <gml:pos>48.424608 -123.2257</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="22.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.7" />
                    <element name="total_precipitation" uom="mm" value="" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="33" />
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
                        <element name="station_name" uom="unitless" value="Entrance Island" />
                        <element name="latitude" uom="degree" value="49.208665" />
                        <element name="longitude" uom="degree" value="-123.810556" />
                        <element name="transport_canada_id" uom="unitless" value="WEL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1022689" />
                        <element name="wmo_station_number" uom="unitless" value="71772" />
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
                            <gml:pos>49.208665 -123.810556</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="23.5" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="17.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="48" />
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
                        <element name="station_name" uom="unitless" value="Esquimalt Harbour" />
                        <element name="latitude" uom="degree" value="48.431972" />
                        <element name="longitude" uom="degree" value="-123.439333" />
                        <element name="transport_canada_id" uom="unitless" value="WPF" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1012710" />
                        <element name="wmo_station_number" uom="unitless" value="71798" />
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
                            <gml:pos>48.431972 -123.439333</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="22.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.4" />
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
                        <element name="station_name" uom="unitless" value="Estevan Point" />
                        <element name="latitude" uom="degree" value="49.383309" />
                        <element name="longitude" uom="degree" value="-126.543109" />
                        <element name="transport_canada_id" uom="unitless" value="WEB" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1032731" />
                        <element name="wmo_station_number" uom="unitless" value="71894" />
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
                            <gml:pos>49.383309 -126.543109</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="18.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.5" />
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
                        <element name="station_name" uom="unitless" value="Fanny Island" />
                        <element name="latitude" uom="degree" value="50.453517" />
                        <element name="longitude" uom="degree" value="-125.992896" />
                        <element name="transport_canada_id" uom="unitless" value="XFA" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1022795" />
                        <element name="wmo_station_number" uom="unitless" value="71568" />
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
                            <gml:pos>50.453517 -125.992896</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="17.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.8" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="61" />
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
                        <element name="station_name" uom="unitless" value="Fort Nelson" />
                        <element name="latitude" uom="degree" value="58.841391" />
                        <element name="longitude" uom="degree" value="-122.574167" />
                        <element name="transport_canada_id" uom="unitless" value="VFN" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 MST" />
                        <element name="climate_station_number" uom="unitless" value="1192948" />
                        <element name="wmo_station_number" uom="unitless" value="71594" />
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
                            <gml:pos>58.841391 -122.574167</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.6" />
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
                        <element name="station_name" uom="unitless" value="Fort Nelson Airport" />
                        <element name="latitude" uom="degree" value="58.836389" />
                        <element name="longitude" uom="degree" value="-122.596944" />
                        <element name="transport_canada_id" uom="unitless" value="YYE" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 MST" />
                        <element name="climate_station_number" uom="unitless" value="1192946" />
                        <element name="wmo_station_number" uom="unitless" value="71945" />
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
                            <gml:pos>58.836389 -122.596944</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.1" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.0" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="0.0" />
                    <element name="snow_amount" uom="cm" value="0.0" />
                    <element name="wind_gust_speed" uom="km/h" value="37" />
                    <element name="wind_direction" uom="code" value="WNW" />
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
                        <element name="station_name" uom="unitless" value="Fort St. James" />
                        <element name="latitude" uom="degree" value="54.455294" />
                        <element name="longitude" uom="degree" value="-124.285557" />
                        <element name="transport_canada_id" uom="unitless" value="VFS" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1092975" />
                        <element name="wmo_station_number" uom="unitless" value="71933" />
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
                            <gml:pos>54.455294 -124.285557</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.5" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="7.8" />
                    <element name="total_precipitation" uom="mm" value="0" />
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
                        <element name="station_name" uom="unitless" value="Fort St. James Golf Club" />
                        <element name="latitude" uom="degree" value="54.459455" />
                        <element name="longitude" uom="degree" value="-124.292502" />
                        <element name="transport_canada_id" uom="unitless" value="VFJ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1092977" />
                        <element name="wmo_station_number" uom="unitless" value="73047" />
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
                            <gml:pos>54.459455 -124.292502</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="24.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="8.1" />
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
                        <element name="station_name" uom="unitless" value="Fort St. John" />
                        <element name="latitude" uom="degree" value="56.247502" />
                        <element name="longitude" uom="degree" value="-120.749724" />
                        <element name="transport_canada_id" uom="unitless" value="VSJ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 MST" />
                        <element name="climate_station_number" uom="unitless" value="1183002" />
                        <element name="wmo_station_number" uom="unitless" value="73090" />
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
                            <gml:pos>56.247502 -120.749724</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="24.1" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.5" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="37" />
                    <element name="wind_direction" uom="code" value="SW" />
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
                        <element name="station_name" uom="unitless" value="Fort St. John Airport" />
                        <element name="latitude" uom="degree" value="56.238333" />
                        <element name="longitude" uom="degree" value="-120.740278" />
                        <element name="transport_canada_id" uom="unitless" value="YXJ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 MST" />
                        <element name="climate_station_number" uom="unitless" value="1183001" />
                        <element name="wmo_station_number" uom="unitless" value="71943" />
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
                            <gml:pos>56.238333 -120.740278</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="24.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.3" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="0.0" />
                    <element name="snow_amount" uom="cm" value="0.0" />
                    <element name="wind_gust_speed" uom="km/h" value="43" />
                    <element name="wind_direction" uom="code" value="WSW" />
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
                        <element name="station_name" uom="unitless" value="Golden" />
                        <element name="latitude" uom="degree" value="51.300222" />
                        <element name="longitude" uom="degree" value="-116.984333" />
                        <element name="transport_canada_id" uom="unitless" value="VGE" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T17:45:00.000 MDT" />
                        <element name="climate_station_number" uom="unitless" value="1173220" />
                        <element name="wmo_station_number" uom="unitless" value="71905" />
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
                            <gml:pos>51.300222 -116.984333</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="8.3" />
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
                        <element name="station_name" uom="unitless" value="Grey Islet" />
                        <element name="latitude" uom="degree" value="54.58032" />
                        <element name="longitude" uom="degree" value="-130.6978" />
                        <element name="transport_canada_id" uom="unitless" value="WEK" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1063303" />
                        <element name="wmo_station_number" uom="unitless" value="71476" />
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
                            <gml:pos>54.58032 -130.6978</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="13.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.9" />
                    <element name="total_precipitation" uom="mm" value="18.8" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="37" />
                    <element name="wind_direction" uom="code" value="ENE" />
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
                        <element name="station_name" uom="unitless" value="Herbert Island" />
                        <element name="latitude" uom="degree" value="50.939761" />
                        <element name="longitude" uom="degree" value="-127.63205" />
                        <element name="transport_canada_id" uom="unitless" value="WLP" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1063461" />
                        <element name="wmo_station_number" uom="unitless" value="71485" />
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
                            <gml:pos>50.939761 -127.63205</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="14.5" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="35" />
                    <element name="wind_direction" uom="code" value="WNW" />
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
                        <element name="station_name" uom="unitless" value="Holland Rock" />
                        <element name="latitude" uom="degree" value="54.172234" />
                        <element name="longitude" uom="degree" value="-130.36085" />
                        <element name="transport_canada_id" uom="unitless" value="WHL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1063496" />
                        <element name="wmo_station_number" uom="unitless" value="71219" />
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
                            <gml:pos>54.172234 -130.36085</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="14.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.9" />
                    <element name="total_precipitation" uom="mm" value="7.8" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="56" />
                    <element name="wind_direction" uom="code" value="SSE" />
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
                        <element name="station_name" uom="unitless" value="Hope" />
                        <element name="latitude" uom="degree" value="49.369833" />
                        <element name="longitude" uom="degree" value="-121.493472" />
                        <element name="transport_canada_id" uom="unitless" value="VPE" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1113543" />
                        <element name="wmo_station_number" uom="unitless" value="71114" />
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
                            <gml:pos>49.369833 -121.493472</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.4" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="33" />
                    <element name="wind_direction" uom="code" value="WNW" />
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
                        <element name="station_name" uom="unitless" value="Hope Airport" />
                        <element name="latitude" uom="degree" value="49.368333" />
                        <element name="longitude" uom="degree" value="-121.498056" />
                        <element name="transport_canada_id" uom="unitless" value="YHE" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1113542" />
                        <element name="wmo_station_number" uom="unitless" value="71187" />
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
                            <gml:pos>49.368333 -121.498056</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="30.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.5" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="43" />
                    <element name="wind_direction" uom="code" value="NW" />
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
                        <element name="station_name" uom="unitless" value="Howe Sound - Pam Rocks" />
                        <element name="latitude" uom="degree" value="49.48778" />
                        <element name="longitude" uom="degree" value="-123.299453" />
                        <element name="transport_canada_id" uom="unitless" value="WAS" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="10459NN" />
                        <element name="wmo_station_number" uom="unitless" value="71211" />
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
                            <gml:pos>49.48778 -123.299453</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="24.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="17.1" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="35" />
                    <element name="wind_direction" uom="code" value="N" />
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
                        <element name="station_name" uom="unitless" value="Kamloops" />
                        <element name="latitude" uom="degree" value="50.702222" />
                        <element name="longitude" uom="degree" value="-120.441944" />
                        <element name="transport_canada_id" uom="unitless" value="ZKA" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1163842" />
                        <element name="wmo_station_number" uom="unitless" value="71741" />
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
                            <gml:pos>50.702222 -120.441944</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="35.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="16.0" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="35" />
                    <element name="wind_direction" uom="code" value="ESE" />
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
                        <element name="station_name" uom="unitless" value="Kamloops Airport" />
                        <element name="latitude" uom="degree" value="50.7025" />
                        <element name="longitude" uom="degree" value="-120.448611" />
                        <element name="transport_canada_id" uom="unitless" value="YKA" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1163781" />
                        <element name="wmo_station_number" uom="unitless" value="71887" />
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
                            <gml:pos>50.7025 -120.448611</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="35.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="15.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="0.0" />
                    <element name="snow_amount" uom="cm" value="0.0" />
                    <element name="wind_gust_speed" uom="km/h" value="35" />
                    <element name="wind_direction" uom="code" value="E" />
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
                        <element name="station_name" uom="unitless" value="Kelowna" />
                        <element name="latitude" uom="degree" value="49.94075" />
                        <element name="longitude" uom="degree" value="-119.400211" />
                        <element name="transport_canada_id" uom="unitless" value="VKU" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1123996" />
                        <element name="wmo_station_number" uom="unitless" value="71644" />
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
                            <gml:pos>49.94075 -119.400211</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="34.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.4" />
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
                        <element name="station_name" uom="unitless" value="Kelowna Airport" />
                        <element name="latitude" uom="degree" value="49.957222" />
                        <element name="longitude" uom="degree" value="-119.377778" />
                        <element name="transport_canada_id" uom="unitless" value="YLW" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1123939" />
                        <element name="wmo_station_number" uom="unitless" value="71203" />
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
                            <gml:pos>49.957222 -119.377778</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="33.5" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.0" />
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
                        <element name="station_name" uom="unitless" value="Kindakun Rocks" />
                        <element name="latitude" uom="degree" value="53.31558" />
                        <element name="longitude" uom="degree" value="-132.772" />
                        <element name="transport_canada_id" uom="unitless" value="WQS" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1054222" />
                        <element name="wmo_station_number" uom="unitless" value="71472" />
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
                            <gml:pos>53.31558 -132.772</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="12.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.4" />
                    <element name="total_precipitation" uom="mm" value="3.8" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="46" />
                    <element name="wind_direction" uom="code" value="SSE" />
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
                        <element name="station_name" uom="unitless" value="Kitimat Forest Ave" />
                        <element name="latitude" uom="degree" value="54.053618" />
                        <element name="longitude" uom="degree" value="-128.633635" />
                        <element name="transport_canada_id" uom="unitless" value="VKC" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1064324" />
                        <element name="wmo_station_number" uom="unitless" value="73007" />
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
                            <gml:pos>54.053618 -128.633635</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="16.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.3" />
                    <element name="total_precipitation" uom="mm" value="5.8" />
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
                        <element name="station_name" uom="unitless" value="Langara Island" />
                        <element name="latitude" uom="degree" value="54.255388" />
                        <element name="longitude" uom="degree" value="-133.058488" />
                        <element name="transport_canada_id" uom="unitless" value="WJU" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1054503" />
                        <element name="wmo_station_number" uom="unitless" value="71903" />
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
                            <gml:pos>54.255388 -133.058488</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="" />
                    <element name="total_precipitation" uom="mm" value="" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="56" />
                    <element name="wind_direction" uom="code" value="S" />
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
                        <element name="station_name" uom="unitless" value="Lillooet" />
                        <element name="latitude" uom="degree" value="50.683728" />
                        <element name="longitude" uom="degree" value="-121.934151" />
                        <element name="transport_canada_id" uom="unitless" value="WKF" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1114619" />
                        <element name="wmo_station_number" uom="unitless" value="71999" />
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
                            <gml:pos>50.683728 -121.934151</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="35.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.5" />
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
                        <element name="station_name" uom="unitless"
                            value="Lucy Islands Lightstation" />
                        <element name="latitude" uom="degree" value="54.29592" />
                        <element name="longitude" uom="degree" value="-130.609" />
                        <element name="transport_canada_id" uom="unitless" value="WLC" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1064728" />
                        <element name="wmo_station_number" uom="unitless" value="71220" />
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
                            <gml:pos>54.29592 -130.609</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="14.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.0" />
                    <element name="total_precipitation" uom="mm" value="" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="46" />
                    <element name="wind_direction" uom="code" value="SE" />
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
                        <element name="station_name" uom="unitless" value="Lytton" />
                        <element name="latitude" uom="degree" value="50.224444" />
                        <element name="longitude" uom="degree" value="-121.581944" />
                        <element name="transport_canada_id" uom="unitless" value="WLY" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1114738" />
                        <element name="wmo_station_number" uom="unitless" value="71812" />
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
                            <gml:pos>50.224444 -121.581944</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="36.1" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.3" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="52" />
                    <element name="wind_direction" uom="code" value="SSW" />
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
                        <element name="station_name" uom="unitless" value="Lytton Climate" />
                        <element name="latitude" uom="degree" value="50.224444" />
                        <element name="longitude" uom="degree" value="-121.581944" />
                        <element name="transport_canada_id" uom="unitless" value="VLY" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1114746" />
                        <element name="wmo_station_number" uom="unitless" value="71765" />
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
                            <gml:pos>50.224444 -121.581944</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="36.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.2" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="46" />
                    <element name="wind_direction" uom="code" value="S" />
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
                        <element name="station_name" uom="unitless" value="Mackenzie" />
                        <element name="latitude" uom="degree" value="55.305289" />
                        <element name="longitude" uom="degree" value="-123.137802" />
                        <element name="transport_canada_id" uom="unitless" value="VZY" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1184793" />
                        <element name="wmo_station_number" uom="unitless" value="71944" />
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
                            <gml:pos>55.305289 -123.137802</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="23.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="7.0" />
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
                        <element name="station_name" uom="unitless" value="Mackenzie Airport" />
                        <element name="latitude" uom="degree" value="55.299444" />
                        <element name="longitude" uom="degree" value="-123.133333" />
                        <element name="transport_canada_id" uom="unitless" value="YZY" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1184791" />
                        <element name="wmo_station_number" uom="unitless" value="71290" />
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
                            <gml:pos>55.299444 -123.133333</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="22.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="6.5" />
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
                        <element name="station_name" uom="unitless" value="Malahat" />
                        <element name="latitude" uom="degree" value="48.574917" />
                        <element name="longitude" uom="degree" value="-123.529917" />
                        <element name="transport_canada_id" uom="unitless" value="WKH" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1014820" />
                        <element name="wmo_station_number" uom="unitless" value="71774" />
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
                            <gml:pos>48.574917 -123.529917</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="16.8" />
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
                        <element name="station_name" uom="unitless" value="Merritt" />
                        <element name="latitude" uom="degree" value="50.112502" />
                        <element name="longitude" uom="degree" value="-120.778056" />
                        <element name="transport_canada_id" uom="unitless" value="VME" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1125073" />
                        <element name="wmo_station_number" uom="unitless" value="71557" />
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
                            <gml:pos>50.112502 -120.778056</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="33.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.0" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="31" />
                    <element name="wind_direction" uom="code" value="S" />
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
                        <element name="station_name" uom="unitless" value="Nakusp" />
                        <element name="latitude" uom="degree" value="50.269425" />
                        <element name="longitude" uom="degree" value="-117.817094" />
                        <element name="transport_canada_id" uom="unitless" value="WNP" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1145297" />
                        <element name="wmo_station_number" uom="unitless" value="71216" />
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
                            <gml:pos>50.269425 -117.817094</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.7" />
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
                        <element name="station_name" uom="unitless" value="Nelson" />
                        <element name="latitude" uom="degree" value="49.491389" />
                        <element name="longitude" uom="degree" value="-117.305278" />
                        <element name="transport_canada_id" uom="unitless" value="WNM" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1145M29" />
                        <element name="wmo_station_number" uom="unitless" value="71776" />
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
                            <gml:pos>49.491389 -117.305278</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="32.9" />
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
                        <element name="station_name" uom="unitless" value="North Cowichan" />
                        <element name="latitude" uom="degree" value="48.824169" />
                        <element name="longitude" uom="degree" value="-123.718891" />
                        <element name="transport_canada_id" uom="unitless" value="VOO" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1015630" />
                        <element name="wmo_station_number" uom="unitless" value="71927" />
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
                            <gml:pos>48.824169 -123.718891</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="31.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.7" />
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
                        <element name="station_name" uom="unitless"
                            value="Ootsa Lake Skins Lake Spillway" />
                        <element name="latitude" uom="degree" value="53.771889" />
                        <element name="longitude" uom="degree" value="-125.996719" />
                        <element name="transport_canada_id" uom="unitless" value="VSL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1085836" />
                        <element name="wmo_station_number" uom="unitless" value="71679" />
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
                            <gml:pos>53.771889 -125.996719</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="20.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="6.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="41" />
                    <element name="wind_direction" uom="code" value="NW" />
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
                        <element name="station_name" uom="unitless" value="Osoyoos" />
                        <element name="latitude" uom="degree" value="49.028292" />
                        <element name="longitude" uom="degree" value="-119.440992" />
                        <element name="transport_canada_id" uom="unitless" value="WYY" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1125852" />
                        <element name="wmo_station_number" uom="unitless" value="71215" />
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
                            <gml:pos>49.028292 -119.440992</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="36.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.2" />
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
                        <element name="station_name" uom="unitless" value="Pemberton Airport" />
                        <element name="latitude" uom="degree" value="50.305646" />
                        <element name="longitude" uom="degree" value="-122.734089" />
                        <element name="transport_canada_id" uom="unitless" value="WGP" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1086082" />
                        <element name="wmo_station_number" uom="unitless" value="71777" />
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
                            <gml:pos>50.305646 -122.734089</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="35.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.6" />
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
                        <element name="station_name" uom="unitless" value="Penticton Airport" />
                        <element name="latitude" uom="degree" value="49.4625" />
                        <element name="longitude" uom="degree" value="-119.602222" />
                        <element name="transport_canada_id" uom="unitless" value="YYF" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1126146" />
                        <element name="wmo_station_number" uom="unitless" value="71889" />
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
                            <gml:pos>49.4625 -119.602222</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="32.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.4" />
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
                        <element name="station_name" uom="unitless" value="Pitt Meadows" />
                        <element name="latitude" uom="degree" value="49.208323" />
                        <element name="longitude" uom="degree" value="-122.690021" />
                        <element name="transport_canada_id" uom="unitless" value="WMM" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1106178" />
                        <element name="wmo_station_number" uom="unitless" value="71775" />
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
                            <gml:pos>49.208323 -122.690021</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="31.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.5" />
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
                        <element name="station_name" uom="unitless" value="Point Atkinson" />
                        <element name="latitude" uom="degree" value="49.330361" />
                        <element name="longitude" uom="degree" value="-123.264722" />
                        <element name="transport_canada_id" uom="unitless" value="WSB" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1106200" />
                        <element name="wmo_station_number" uom="unitless" value="71037" />
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
                            <gml:pos>49.330361 -123.264722</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="23.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="16.2" />
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
                        <element name="station_name" uom="unitless" value="Port Alberni" />
                        <element name="latitude" uom="degree" value="49.316583" />
                        <element name="longitude" uom="degree" value="-124.926833" />
                        <element name="transport_canada_id" uom="unitless" value="WQC" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1036B06" />
                        <element name="wmo_station_number" uom="unitless" value="71475" />
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
                            <gml:pos>49.316583 -124.926833</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="33.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.0" />
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
                        <element name="station_name" uom="unitless" value="Port Hardy" />
                        <element name="latitude" uom="degree" value="50.684458" />
                        <element name="longitude" uom="degree" value="-127.376945" />
                        <element name="transport_canada_id" uom="unitless" value="VHD" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1026273" />
                        <element name="wmo_station_number" uom="unitless" value="73014" />
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
                            <gml:pos>50.684458 -127.376945</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="19.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="8.7" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="31" />
                    <element name="wind_direction" uom="code" value="NNW" />
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
                        <element name="station_name" uom="unitless" value="Port Hardy Airport" />
                        <element name="latitude" uom="degree" value="50.680556" />
                        <element name="longitude" uom="degree" value="-127.366667" />
                        <element name="transport_canada_id" uom="unitless" value="YZT" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1026271" />
                        <element name="wmo_station_number" uom="unitless" value="71109" />
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
                            <gml:pos>50.680556 -127.366667</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="20.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="8.2" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="0.0" />
                    <element name="snow_amount" uom="cm" value="0.0" />
                    <element name="wind_gust_speed" uom="km/h" value="39" />
                    <element name="wind_direction" uom="code" value="NNW" />
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
                        <element name="station_name" uom="unitless" value="Port Mellon" />
                        <element name="latitude" uom="degree" value="49.526306" />
                        <element name="longitude" uom="degree" value="-123.49625" />
                        <element name="transport_canada_id" uom="unitless" value="VOM" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1046332" />
                        <element name="wmo_station_number" uom="unitless" value="71605" />
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
                            <gml:pos>49.526306 -123.49625</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="15.0" />
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
                        <element name="station_name" uom="unitless" value="Powell River" />
                        <element name="latitude" uom="degree" value="49.834556" />
                        <element name="longitude" uom="degree" value="-124.496806" />
                        <element name="transport_canada_id" uom="unitless" value="VOP" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1046392" />
                        <element name="wmo_station_number" uom="unitless" value="71720" />
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
                            <gml:pos>49.834556 -124.496806</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="27.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.3" />
                    <element name="total_precipitation" uom="mm" value="0.4" />
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
                        <element name="station_name" uom="unitless" value="Prince George" />
                        <element name="latitude" uom="degree" value="53.888889" />
                        <element name="longitude" uom="degree" value="-122.671945" />
                        <element name="transport_canada_id" uom="unitless" value="VXS" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1096453" />
                        <element name="wmo_station_number" uom="unitless" value="71302" />
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
                            <gml:pos>53.888889 -122.671945</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.5" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.1" />
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
                        <element name="station_name" uom="unitless" value="Prince George Airport" />
                        <element name="latitude" uom="degree" value="53.884167" />
                        <element name="longitude" uom="degree" value="-122.6775" />
                        <element name="transport_canada_id" uom="unitless" value="YXS" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1096439" />
                        <element name="wmo_station_number" uom="unitless" value="71896" />
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
                            <gml:pos>53.884167 -122.6775</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.9" />
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
                        <element name="station_name" uom="unitless" value="Prince Rupert Airport" />
                        <element name="latitude" uom="degree" value="54.286111" />
                        <element name="longitude" uom="degree" value="-130.444722" />
                        <element name="transport_canada_id" uom="unitless" value="YPR" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1066482" />
                        <element name="wmo_station_number" uom="unitless" value="71022" />
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
                            <gml:pos>54.286111 -130.444722</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="15.5" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.6" />
                    <element name="total_precipitation" uom="mm" value="16.6" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="35" />
                    <element name="wind_direction" uom="code" value="SSE" />
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
                        <element name="station_name" uom="unitless" value="Princeton" />
                        <element name="latitude" uom="degree" value="49.465" />
                        <element name="longitude" uom="degree" value="-120.51" />
                        <element name="transport_canada_id" uom="unitless" value="WPR" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="112FN0M" />
                        <element name="wmo_station_number" uom="unitless" value="71032" />
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
                            <gml:pos>49.465 -120.51</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="34.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="43" />
                    <element name="wind_direction" uom="code" value="WNW" />
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
                        <element name="station_name" uom="unitless" value="Puntzi Mountain" />
                        <element name="latitude" uom="degree" value="52.114444" />
                        <element name="longitude" uom="degree" value="-124.135556" />
                        <element name="transport_canada_id" uom="unitless" value="WPU" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1086558" />
                        <element name="wmo_station_number" uom="unitless" value="71050" />
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
                            <gml:pos>52.114444 -124.135556</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="5.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="46" />
                    <element name="wind_direction" uom="code" value="SE" />
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
                        <element name="station_name" uom="unitless" value="Qualicum Beach Airport" />
                        <element name="latitude" uom="degree" value="49.337222" />
                        <element name="longitude" uom="degree" value="-124.393889" />
                        <element name="transport_canada_id" uom="unitless" value="VOQ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1026562" />
                        <element name="wmo_station_number" uom="unitless" value="71766" />
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
                            <gml:pos>49.337222 -124.393889</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="14.2" />
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
                        <element name="station_name" uom="unitless" value="Quesnel" />
                        <element name="latitude" uom="degree" value="53.026669" />
                        <element name="longitude" uom="degree" value="-122.506391" />
                        <element name="transport_canada_id" uom="unitless" value="VQZ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1096631" />
                        <element name="wmo_station_number" uom="unitless" value="71779" />
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
                            <gml:pos>53.026669 -122.506391</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="8.8" />
                    <element name="total_precipitation" uom="mm" value="0.7" />
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
                        <element name="station_name" uom="unitless" value="Quesnel Airport" />
                        <element name="latitude" uom="degree" value="53.026111" />
                        <element name="longitude" uom="degree" value="-122.510278" />
                        <element name="transport_canada_id" uom="unitless" value="YQZ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1096629" />
                        <element name="wmo_station_number" uom="unitless" value="71192" />
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
                            <gml:pos>53.026111 -122.510278</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="8.4" />
                    <element name="total_precipitation" uom="mm" value="0.7" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="31" />
                    <element name="wind_direction" uom="code" value="NNW" />
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
                        <element name="station_name" uom="unitless" value="Race Rocks Lightstation" />
                        <element name="latitude" uom="degree" value="48.297984" />
                        <element name="longitude" uom="degree" value="-123.531441" />
                        <element name="transport_canada_id" uom="unitless" value="WQK" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1016640" />
                        <element name="wmo_station_number" uom="unitless" value="71778" />
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
                            <gml:pos>48.297984 -123.531441</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="16.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.3" />
                    <element name="total_precipitation" uom="mm" value="" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="76" />
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
                        <element name="station_name" uom="unitless" value="Revelstoke" />
                        <element name="latitude" uom="degree" value="50.958222" />
                        <element name="longitude" uom="degree" value="-118.176278" />
                        <element name="transport_canada_id" uom="unitless" value="VRA" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1176755" />
                        <element name="wmo_station_number" uom="unitless" value="71882" />
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
                            <gml:pos>50.958222 -118.176278</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="30.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="11.0" />
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
                        <element name="station_name" uom="unitless" value="Revelstoke Airport" />
                        <element name="latitude" uom="degree" value="50.966667" />
                        <element name="longitude" uom="degree" value="-118.183333" />
                        <element name="transport_canada_id" uom="unitless" value="YRV" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1176745" />
                        <element name="wmo_station_number" uom="unitless" value="71685" />
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
                            <gml:pos>50.966667 -118.183333</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="30.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.9" />
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
                        <element name="station_name" uom="unitless" value="Rose Spit" />
                        <element name="latitude" uom="degree" value="54.15914" />
                        <element name="longitude" uom="degree" value="-131.661326" />
                        <element name="transport_canada_id" uom="unitless" value="WRO" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1056869" />
                        <element name="wmo_station_number" uom="unitless" value="71477" />
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
                            <gml:pos>54.15914 -131.661326</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="17.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.0" />
                    <element name="total_precipitation" uom="mm" value="5.8" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="52" />
                    <element name="wind_direction" uom="code" value="SSE" />
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
                        <element name="station_name" uom="unitless" value="Saanichton CFIA" />
                        <element name="latitude" uom="degree" value="48.621667" />
                        <element name="longitude" uom="degree" value="-123.418889" />
                        <element name="transport_canada_id" uom="unitless" value="VSA" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1016943" />
                        <element name="wmo_station_number" uom="unitless" value="73028" />
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
                            <gml:pos>48.621667 -123.418889</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.1" />
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
                        <element name="station_name" uom="unitless" value="Salmon Arm" />
                        <element name="latitude" uom="degree" value="50.703" />
                        <element name="longitude" uom="degree" value="-119.290678" />
                        <element name="transport_canada_id" uom="unitless" value="WSL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="116FRMN" />
                        <element name="wmo_station_number" uom="unitless" value="71218" />
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
                            <gml:pos>50.703 -119.290678</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.6" />
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
                        <element name="station_name" uom="unitless" value="Sand Heads Lightstation" />
                        <element name="latitude" uom="degree" value="49.105896" />
                        <element name="longitude" uom="degree" value="-123.303367" />
                        <element name="transport_canada_id" uom="unitless" value="WVF" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1107010" />
                        <element name="wmo_station_number" uom="unitless" value="71209" />
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
                            <gml:pos>49.105896 -123.303367</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="23.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="17.1" />
                    <element name="total_precipitation" uom="mm" value="" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="35" />
                    <element name="wind_direction" uom="code" value="NW" />
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
                        <element name="station_name" uom="unitless" value="Sandspit" />
                        <element name="latitude" uom="degree" value="53.249445" />
                        <element name="longitude" uom="degree" value="-131.813127" />
                        <element name="transport_canada_id" uom="unitless" value="VZP" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1057051" />
                        <element name="wmo_station_number" uom="unitless" value="71101" />
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
                            <gml:pos>53.249445 -131.813127</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="17.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.4" />
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
                        <element name="station_name" uom="unitless" value="Sandspit Airport" />
                        <element name="latitude" uom="degree" value="53.254167" />
                        <element name="longitude" uom="degree" value="-131.813889" />
                        <element name="transport_canada_id" uom="unitless" value="YZP" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1057052" />
                        <element name="wmo_station_number" uom="unitless" value="71111" />
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
                            <gml:pos>53.254167 -131.813889</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="17.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.5" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="37" />
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
                        <element name="station_name" uom="unitless" value="Sartine Island" />
                        <element name="latitude" uom="degree" value="50.821111" />
                        <element name="longitude" uom="degree" value="-128.908056" />
                        <element name="transport_canada_id" uom="unitless" value="WFG" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1037090" />
                        <element name="wmo_station_number" uom="unitless" value="71478" />
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
                            <gml:pos>50.821111 -128.908056</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="16.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.9" />
                    <element name="total_precipitation" uom="mm" value="0.4" />
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
                        <element name="station_name" uom="unitless" value="Saturna Capmon" />
                        <element name="latitude" uom="degree" value="48.775022" />
                        <element name="longitude" uom="degree" value="-123.128078" />
                        <element name="transport_canada_id" uom="unitless" value="VTS" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1017099" />
                        <element name="wmo_station_number" uom="unitless" value="71914" />
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
                            <gml:pos>48.775022 -123.128078</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="27.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="16.9" />
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
                        <element name="station_name" uom="unitless" value="Saturna Island" />
                        <element name="latitude" uom="degree" value="48.783907" />
                        <element name="longitude" uom="degree" value="-123.044745" />
                        <element name="transport_canada_id" uom="unitless" value="WEZ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1017101" />
                        <element name="wmo_station_number" uom="unitless" value="71473" />
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
                            <gml:pos>48.783907 -123.044745</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.5" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="15.0" />
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
                        <element name="station_name" uom="unitless" value="Sechelt" />
                        <element name="latitude" uom="degree" value="49.457997" />
                        <element name="longitude" uom="degree" value="-123.715262" />
                        <element name="transport_canada_id" uom="unitless" value="VOU" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1047172" />
                        <element name="wmo_station_number" uom="unitless" value="71638" />
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
                            <gml:pos>49.457997 -123.715262</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.4" />
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
                        <element name="station_name" uom="unitless" value="Sheringham Point" />
                        <element name="latitude" uom="degree" value="48.376694" />
                        <element name="longitude" uom="degree" value="-123.921028" />
                        <element name="transport_canada_id" uom="unitless" value="WSP" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1017254" />
                        <element name="wmo_station_number" uom="unitless" value="71780" />
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
                            <gml:pos>48.376694 -123.921028</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="13.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.2" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="52" />
                    <element name="wind_direction" uom="code" value="WNW" />
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
                        <element name="station_name" uom="unitless" value="Sisters Islets" />
                        <element name="latitude" uom="degree" value="49.486611" />
                        <element name="longitude" uom="degree" value="-124.434944" />
                        <element name="transport_canada_id" uom="unitless" value="WGT" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1027403" />
                        <element name="wmo_station_number" uom="unitless" value="71781" />
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
                            <gml:pos>49.486611 -124.434944</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="17.0" />
                    <element name="total_precipitation" uom="mm" value="" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="37" />
                    <element name="wind_direction" uom="code" value="NW" />
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
                        <element name="station_name" uom="unitless" value="Smithers" />
                        <element name="latitude" uom="degree" value="54.824167" />
                        <element name="longitude" uom="degree" value="-127.189444" />
                        <element name="transport_canada_id" uom="unitless" value="VYD" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1077501" />
                        <element name="wmo_station_number" uom="unitless" value="71268" />
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
                            <gml:pos>54.824167 -127.189444</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="20.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.8" />
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
                        <element name="station_name" uom="unitless" value="Smithers Airport" />
                        <element name="latitude" uom="degree" value="54.825278" />
                        <element name="longitude" uom="degree" value="-127.182778" />
                        <element name="transport_canada_id" uom="unitless" value="YYD" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1077498" />
                        <element name="wmo_station_number" uom="unitless" value="" />
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
                            <gml:pos>54.825278 -127.182778</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="20.1" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.2" />
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
                        <element name="station_name" uom="unitless" value="Solander Island" />
                        <element name="latitude" uom="degree" value="50.11151" />
                        <element name="longitude" uom="degree" value="-127.94" />
                        <element name="transport_canada_id" uom="unitless" value="WRU" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1037553" />
                        <element name="wmo_station_number" uom="unitless" value="71479" />
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
                            <gml:pos>50.11151 -127.94</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="14.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="10.6" />
                    <element name="total_precipitation" uom="mm" value="0.4" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="54" />
                    <element name="wind_direction" uom="code" value="ENE" />
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
                        <element name="station_name" uom="unitless" value="Sparwood" />
                        <element name="latitude" uom="degree" value="49.745" />
                        <element name="longitude" uom="degree" value="-114.8839" />
                        <element name="transport_canada_id" uom="unitless" value="WGW" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T17:45:00.000 MDT" />
                        <element name="climate_station_number" uom="unitless" value="1157631" />
                        <element name="wmo_station_number" uom="unitless" value="71782" />
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
                            <gml:pos>49.745 -114.8839</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="5.9" />
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
                        <element name="station_name" uom="unitless" value="Squamish Airport" />
                        <element name="latitude" uom="degree" value="49.783208" />
                        <element name="longitude" uom="degree" value="-123.161194" />
                        <element name="transport_canada_id" uom="unitless" value="WSK" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="10476F0" />
                        <element name="wmo_station_number" uom="unitless" value="71207" />
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
                            <gml:pos>49.783208 -123.161194</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="30.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.1" />
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
                        <element name="station_name" uom="unitless" value="Summerland" />
                        <element name="latitude" uom="degree" value="49.562556" />
                        <element name="longitude" uom="degree" value="-119.648694" />
                        <element name="transport_canada_id" uom="unitless" value="WUS" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="112G8L1" />
                        <element name="wmo_station_number" uom="unitless" value="71768" />
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
                            <gml:pos>49.562556 -119.648694</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="31.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="15.1" />
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
                        <element name="station_name" uom="unitless" value="Tatlayoko Lake" />
                        <element name="latitude" uom="degree" value="51.674556" />
                        <element name="longitude" uom="degree" value="-124.403139" />
                        <element name="transport_canada_id" uom="unitless" value="XTL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1088015" />
                        <element name="wmo_station_number" uom="unitless" value="71028" />
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
                            <gml:pos>51.674556 -124.403139</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="29.4" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="6.0" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="33" />
                    <element name="wind_direction" uom="code" value="S" />
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
                        <element name="station_name" uom="unitless" value="Terrace Airport" />
                        <element name="latitude" uom="degree" value="54.468611" />
                        <element name="longitude" uom="degree" value="-128.578333" />
                        <element name="transport_canada_id" uom="unitless" value="YXT" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1068134" />
                        <element name="wmo_station_number" uom="unitless" value="71951" />
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
                            <gml:pos>54.468611 -128.578333</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="18.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.0" />
                    <element name="total_precipitation" uom="mm" value="1.2" />
                    <element name="rain_amount" uom="mm" value="1.2" />
                    <element name="snow_amount" uom="cm" value="0.0" />
                    <element name="wind_gust_speed" uom="km/h" value="43" />
                    <element name="wind_direction" uom="code" value="SSE" />
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
                        <element name="station_name" uom="unitless" value="University of Victoria" />
                        <element name="latitude" uom="degree" value="48.457" />
                        <element name="longitude" uom="degree" value="-123.304611" />
                        <element name="transport_canada_id" uom="unitless" value="WYJ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1018598" />
                        <element name="wmo_station_number" uom="unitless" value="71783" />
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
                            <gml:pos>48.457 -123.304611</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="27.7" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.0" />
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
                        <element name="station_name" uom="unitless" value="Vancouver" />
                        <element name="latitude" uom="degree" value="49.1825" />
                        <element name="longitude" uom="degree" value="-123.187236" />
                        <element name="transport_canada_id" uom="unitless" value="VVR" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1108380" />
                        <element name="wmo_station_number" uom="unitless" value="71608" />
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
                            <gml:pos>49.1825 -123.187236</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="24.3" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.7" />
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
                        <element name="station_name" uom="unitless" value="Vancouver Harbour" />
                        <element name="latitude" uom="degree" value="49.295353" />
                        <element name="longitude" uom="degree" value="-123.121869" />
                        <element name="transport_canada_id" uom="unitless" value="WHC" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1108446" />
                        <element name="wmo_station_number" uom="unitless" value="71201" />
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
                            <gml:pos>49.295353 -123.121869</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.5" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.9" />
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
                        <element name="station_name" uom="unitless" value="Vancouver Int'l Airport" />
                        <element name="latitude" uom="degree" value="49.194722" />
                        <element name="longitude" uom="degree" value="-123.183889" />
                        <element name="transport_canada_id" uom="unitless" value="YVR" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1108395" />
                        <element name="wmo_station_number" uom="unitless" value="71892" />
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
                            <gml:pos>49.194722 -123.183889</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="24.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.4" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="0.0" />
                    <element name="snow_amount" uom="cm" value="0.0" />
                    <element name="wind_gust_speed" uom="km/h" value="33" />
                    <element name="wind_direction" uom="code" value="WNW" />
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
                        <element name="station_name" uom="unitless" value="Vernon" />
                        <element name="latitude" uom="degree" value="50.223306" />
                        <element name="longitude" uom="degree" value="-119.193528" />
                        <element name="transport_canada_id" uom="unitless" value="WJV" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1128582" />
                        <element name="wmo_station_number" uom="unitless" value="71115" />
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
                            <gml:pos>50.223306 -119.193528</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="34.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.7" />
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
                        <element name="station_name" uom="unitless" value="Victoria Gonzales" />
                        <element name="latitude" uom="degree" value="48.413304" />
                        <element name="longitude" uom="degree" value="-123.324776" />
                        <element name="transport_canada_id" uom="unitless" value="WLM" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1018611" />
                        <element name="wmo_station_number" uom="unitless" value="71200" />
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
                            <gml:pos>48.413304 -123.324776</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="21.0" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.6" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="39" />
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
                        <element name="station_name" uom="unitless" value="Victoria Int'l Airport" />
                        <element name="latitude" uom="degree" value="48.647222" />
                        <element name="longitude" uom="degree" value="-123.425833" />
                        <element name="transport_canada_id" uom="unitless" value="YYJ" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1018621" />
                        <element name="wmo_station_number" uom="unitless" value="71799" />
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
                            <gml:pos>48.647222 -123.425833</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="26.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.9" />
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
                        <element name="station_name" uom="unitless" value="Warfield" />
                        <element name="latitude" uom="degree" value="49.111944" />
                        <element name="longitude" uom="degree" value="-117.738889" />
                        <element name="transport_canada_id" uom="unitless" value="XWF" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1148705" />
                        <element name="wmo_station_number" uom="unitless" value="71401" />
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
                            <gml:pos>49.111944 -117.738889</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="34.8" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.9" />
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
                        <element name="station_name" uom="unitless" value="West Vancouver" />
                        <element name="latitude" uom="degree" value="49.347042" />
                        <element name="longitude" uom="degree" value="-123.193308" />
                        <element name="transport_canada_id" uom="unitless" value="WWA" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1108824" />
                        <element name="wmo_station_number" uom="unitless" value="71784" />
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
                            <gml:pos>49.347042 -123.193308</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="16.1" />
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
                        <element name="station_name" uom="unitless" value="Whistler - Nesters" />
                        <element name="latitude" uom="degree" value="50.128944" />
                        <element name="longitude" uom="degree" value="-122.954611" />
                        <element name="transport_canada_id" uom="unitless" value="VOC" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1100875" />
                        <element name="wmo_station_number" uom="unitless" value="71687" />
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
                            <gml:pos>50.128944 -122.954611</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="31.2" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="9.1" />
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
                        <element name="station_name" uom="unitless" value="White Rock" />
                        <element name="latitude" uom="degree" value="49.018056" />
                        <element name="longitude" uom="degree" value="-122.783889" />
                        <element name="transport_canada_id" uom="unitless" value="WWK" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1108910" />
                        <element name="wmo_station_number" uom="unitless" value="71785" />
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
                            <gml:pos>49.018056 -122.783889</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="23.6" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="13.1" />
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
                        <element name="station_name" uom="unitless" value="Williams Lake Airport" />
                        <element name="latitude" uom="degree" value="52.183333" />
                        <element name="longitude" uom="degree" value="-122.054444" />
                        <element name="transport_canada_id" uom="unitless" value="YWL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T16:45:00.000 PDT" />
                        <element name="climate_station_number" uom="unitless" value="1098941" />
                        <element name="wmo_station_number" uom="unitless" value="71104" />
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
                            <gml:pos>52.183333 -122.054444</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="28.1" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="12.0" />
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
                        <element name="station_name" uom="unitless" value="Yoho National Park" />
                        <element name="latitude" uom="degree" value="51.442889" />
                        <element name="longitude" uom="degree" value="-116.344556" />
                        <element name="transport_canada_id" uom="unitless" value="WYL" />
                        <element name="observation_date_utc" uom="unitless"
                            value="2025-07-01T23:45:00.000Z" />
                        <element name="observation_date_local_time" uom="unitless"
                            value="2025-07-01T17:45:00.000 MDT" />
                        <element name="climate_station_number" uom="unitless" value="11790J1" />
                        <element name="wmo_station_number" uom="unitless" value="71786" />
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
                            <gml:pos>51.442889 -116.344556</gml:pos>
                        </gml:Point>
                    </gml:location>
                </gml:FeatureCollection>
            </om:featureOfInterest>
            <om:result>
                <elements>
                    <element name="air_temperature_yesterday_high" uom="Celsius" value="25.9" />
                    <element name="air_temperature_yesterday_low" uom="Celsius" value="2.9" />
                    <element name="total_precipitation" uom="mm" value="0.0" />
                    <element name="rain_amount" uom="mm" value="" />
                    <element name="snow_amount" uom="cm" value="" />
                    <element name="wind_gust_speed" uom="km/h" value="" />
                    <element name="wind_direction" uom="code" value="" />
                </elements>
            </om:result>
        </om:Observation>
    </om:member>
</om:ObservationCollection>
"""
)
