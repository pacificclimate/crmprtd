from io import BytesIO
import datetime

import pytz

from crmprtd.networks.crd.normalize import normalize


def test_normalize_good_data():
    lines = b"""{
    "HEADER": {
        "_units": {
            "RainUnit": "millimetre",
            "PrecipitationUnit": "millimetre",
            "AirTemperatureUnit": "Celsius",
            "RelativeHumidityUnit": "percent",
            "WindSpeedUnit": "kilometres per hour",
            "WindDirectionUnit": "degree",
            "SnowDepthUnit": "metre",
            "SnowWaterEquivalentUnit": "millimetre",
            "BarometricPressureUnit": "hectopascal",
            "SolarRadiationUnit": "watt per square metre",
            "SolarActiveRadiationUnit": "micromoles per square metre per second"
        },
        "_info": "IMPORTANT NOTICE - DISCLAIMER - PLEASE READ CAREFULLY -- The Capital Regional District ('CRD') does not warrant or represent that the information contained in the data provided (the 'Information') is free from errors or omissions.  The Information is provide 'AS IS' and made available to the User on the condition that the CRD will not be liable to the User for any loss, damage, cost or expense whatsoever incurred by the User or any other person or entity using or relying on the Information, whether it is caused by or results from any error, negligent act, omission or misrepresentation by the CRD, its officers, employees, agents, contractors or consultants.  The use of the Information by the User or any other person or entity, will be entirely at their sole risk.",
        "_disclaimerDocument": "https://webservices.crd.bc.ca/weatherdata/resources/CRDWeatherDataShareInstructions.pdf"
    },
    "DATA": [
        {
            "RecordID": "14G+20251118000000",
            "StationName": "14g",
            "DateTime": 45979.0,
            "DateTimeString": "20251118000000",
            "Rain": 0.0,
            "Precipitation": 0.1,
            "AirTemperature": 2.7,
            "RelativeHumidity": 100.0,
            "WindSpeed": 3.9,
            "WindDirection": 347.0,
            "SnowDepth": 0.001,
            "SnowWaterEquivalent": -9999.0,
            "BarometricPressure": -9999.0,
            "SolarRadiation": 0.0,
            "SolarActiveRadiation": -9999.0,
            "DataErrors": ""
        }
    ],
    "ERROR": ""
}
"""  # noqa
    tz = pytz.timezone("Canada/Pacific")
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 8
    for row in rows:
        assert row.unit in ("millimetre", "Celsius", "percent", "kilometres per hour", "degree", "metre", "hectopascal", "watt per square metre", "micromoles per square metre per second")
        assert row.station_id == "14g"
        assert row.variable_name in ("Rain", "Precipitation", "AirTemperature", "RelativeHumidity", "WindSpeed", "WindDirection", "SnowDepth", "BarometricPressure", "SolarRadiation", "SolarActiveRadiation")
        assert row.time == tz.localize(datetime.datetime(2025, 11, 18, 00))
