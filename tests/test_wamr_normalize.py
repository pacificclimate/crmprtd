from io import BytesIO

from crmprtd.wamr.normalize import normalize

import pytest


good_data = (
    b"""DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,REPORTED_VALUE
2018-07-30 14:00,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,11.68,% RH,1,n/a,Data Ok,11.7
2018-07-30 13:00,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,17.62,% RH,1,n/a,Data Ok,17.6
2018-07-30 12:00,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,21.76,% RH,1,n/a,Data Ok,21.8
2018-07-30 11:00,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,27.87,% RH,1,n/a,Data Ok,27.9
2018-07-30 10:00,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,34.03,% RH,1,n/a,Data Ok,34.0
""",  # noqa
    b"""DATE_PST,STATION_NAME,RAW_VALUE,REPORTED_VALUE,INSTRUMENT,UNITS,PARAMETER,EMS_ID,LATITUDE,LONGITUDE
2020-07-04 22:00,Abbotsford A Columbia Street,80.7,80.7,HUMIDITY,% RH,HUMIDITY,E289309,49.0215,-122.3266
2020-07-04 21:00,Abbotsford A Columbia Street,71.1,71.1,HUMIDITY,% RH,HUMIDITY,E289309,49.0215,-122.3266
2020-07-04 20:00,Abbotsford A Columbia Street,66.23,66.2,HUMIDITY,% RH,HUMIDITY,E289309,49.0215,-122.3266
2020-07-04 19:00,Abbotsford A Columbia Street,56.3,56.3,HUMIDITY,% RH,HUMIDITY,E289309,49.0215,-122.3266
2020-07-04 18:00,Abbotsford A Columbia Street,51.67,51.7,HUMIDITY,% RH,HUMIDITY,E289309,49.0215,-122.3266
""",  # noqa
)


@pytest.mark.parametrize(("lines"), good_data)
def test_normalize_good_data(lines):
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 5
    for row in rows:
        assert row.unit == "%"


def test_normalize_missing_value():
    lines = b"""DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,REPORTED_VALUE
2018-07-30 14:00,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,,% RH,1,n/a,Data Ok,
"""  # noqa
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 0


def test_normalize_raw_fallback():
    """This input line doesn't have a REPORTED_VALUE but falls back to the
    RAW_VALUE"""
    lines = b"""DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,REPORTED_VALUE
2018-07-30 14:00,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,11.68,% RH,1,n/a,Data Ok,
"""  # noqa
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 1


def test_normalize_bad_value():
    lines = b"""DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,REPORTED_VALUE
2018-07-30 14:00,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,11.68,% RH,1,n/a,Data Ok,bad_val
"""  # noqa
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 0


def test_normalize_bad_date():
    lines = b"""DATE_PST,EMS_ID,STATION_NAME,PARAMETER,AIR_PARAMETER,INSTRUMENT,RAW_VALUE,UNIT,STATUS,AIRCODESTATUS,STATUS_DESCRIPTION,REPORTED_VALUE
BAD_DATE,0250009,Trail Butler Park Met_60,HUMIDITY,HUMIDITY,HUMIDITY,11.68,% RH,1,n/a,Data Ok,11.7
"""  # noqa
    rows = [row for row in normalize(BytesIO(lines))]
    assert len(rows) == 0
