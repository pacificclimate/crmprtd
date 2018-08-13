from io import StringIO
from datetime import datetime
import pytz

from crmprtd.wmb.normalize import normalize


def test_normalize_good_data():
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,2018052711,.00,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
''' # noqa
    rows = [row for row in normalize(StringIO(lines))]
    tz = pytz.timezone('Canada/Pacific')
    assert len(rows) == 17
    for row in rows:
        assert row.station_id == '11'
        assert row.time == datetime.strptime('2018052710',
                                             "%Y%m%d%H").replace(tzinfo=tz)
        assert row.variable_name is not None
        assert row.val is not None
        assert row.network_name is not None


def test_normalize_bad_date():
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,2018052799,.00,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
''' # noqa
    rows = [row for row in normalize(StringIO(lines))]
    assert len(rows) == 0


def test_normalize_bad_value():
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,2018052711,BAD_VAL,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
''' # noqa
    rows = [row for row in normalize(StringIO(lines))]
    assert len(rows) == 16
    tz = pytz.timezone('Canada/Pacific')
    for row in rows:
        assert row.station_id == '11'
        assert row.time == datetime.strptime('2018052710',
                                             "%Y%m%d%H").replace(tzinfo=tz)
        assert row.variable_name is not None
        assert row.val is not None
        assert row.network_name is not None
