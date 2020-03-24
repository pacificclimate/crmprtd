from io import BytesIO
import datetime

import pytz

from crmprtd.crd.normalize import normalize


def test_normalize_good_data():
    lines = b'''{
    "HEADER": {
        "_units": {
            "RainUnit": "millimetre",
            "PrecipitationUnit": "millimetre",
            "AirTemperatureUnit": "Celsius",
            "WindSpeedUnit": "kilometres per hour"
        },
        "_info": "",
        "_disclaimerDocument": "https://webservices.crd.bc.ca/weatherdata/resources/CRDWeatherDataShareInstructions.pdf"
    },
    "DATA": [
        {
            "RecordID": "14G+20200316110000",
            "StationName": "14g",
            "DateTime": 43906.4583333333,
            "DateTimeString": "20200316110000",
            "Rain": 0.0,
            "Precipitation": 1.0,
            "AirTemperature": -9999,
            "WindSpeed": null
        }
    ],
    "ERROR": ""
}
''' # noqa
    tz = pytz.timezone('Canada/Pacific')
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 2
    for row in rows:
        assert row.unit == "millimetre"
        assert row.station_id == "14g"
        assert row.variable_name in ("Rain", "Precipitation")
        assert row.time == tz.localize(datetime.datetime(2020, 3, 16, 11))
