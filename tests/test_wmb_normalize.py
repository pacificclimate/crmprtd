from io import StringIO

from crmprtd.wmb.normalize import normalize


def test_normalize_good_data():
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,2018052711,.00,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052712,.00,16.4,57,9.1,152,81.667679,2.166688,5.4912086,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052713,.00,16.9,54,11.3,185,82.228363,2.5902824,6.5181026,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052714,.00,17.8,53,10.5,185,82.773972,2.6630962,6.9062028,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052715,.00,17.4,50,8.2,161,83.291313,2.5341561,6.5958676,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0
''' # noqa
    f = StringIO(lines)
    rows = [row for row in normalize(f)]
    assert len(rows) == 85


def test_normalize_bad_date():
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,BAD_DATE,.00,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,BAD_DATE,.00,16.4,57,9.1,152,81.667679,2.166688,5.4912086,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,BAD_DATE,.00,16.9,54,11.3,185,82.228363,2.5902824,6.5181026,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,BAD_DATE,.00,17.8,53,10.5,185,82.773972,2.6630962,6.9062028,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052715,.00,17.4,50,8.2,161,83.291313,2.5341561,6.5958676,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0
''' # noqa
    f = StringIO(lines)
    rows = [row for row in normalize(f)]
    assert len(rows) == 17


def test_normalize_bad_value():
    lines = '''station_code,weather_date,precipitation,temperature,relative_humidity,wind_speed,wind_direction,ffmc,isi,fwi,rn_1_pluvio1,snow_depth,snow_depth_quality,precip_pluvio1_status,precip_pluvio1_total,rn_1_pluvio2,precip_pluvio2_status,precip_pluvio2_total,rn_1_RIT,precip_RIT_Status,precip_RIT_total,precip_rgt,solar_radiation_LICOR,solar_radiation_CM3
11,2018052711,BAD_VAL,14.2,55,10.4,167,81.160995,2.1806495,5.5260615,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052712,BAD_VAL,16.4,57,9.1,152,81.667679,2.166688,5.4912086,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052713,BAD_VAL,16.9,54,11.3,185,82.228363,2.5902824,6.5181026,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052714,BAD_VAL,17.8,53,10.5,185,82.773972,2.6630962,6.9062028,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0,
11,2018052715,BAD_VAL,17.4,50,8.2,161,83.291313,2.5341561,6.5958676,.00,.00,,,.00,.00,,.00,.00,.00,.00,,.0
''' # noqa
    f = StringIO(lines)
    rows = [row for row in normalize(f)]
    assert len(rows) == 80
