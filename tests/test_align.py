import pytest
from datetime import datetime
from geoalchemy2.functions import ST_X, ST_Y

import logging

from tests.conftest import records_contain_db_connection

from crmprtd.align import (
    get_network,
    find_or_create_matching_history_and_station,
    get_variable,
    convert_obs_value_to_db_units,
    align,
    histories_within_threshold,
    convert_unit,
)
from crmprtd import Row
from pycds import Station, History


@pytest.mark.parametrize(
    ("network_name", "expected"), [("FLNRO-WMB", True), ("WMB", False)]
)
def test_is_network(test_session, network_name, expected):
    assert bool(get_network(test_session, network_name)) == expected


def test_get_history_with_no_matches(test_session, caplog):
    caplog.set_level(logging.DEBUG, "crmprtd")
    # this observation will not match any in test session
    obs_tuple = Row(
        time=datetime.now(),
        val=123,
        variable_name="relative_humidity",
        unit="percent",
        network_name="FLNRO-WMB",
        station_id="666",
        lat=None,
        lon=None,
    )

    history = find_or_create_matching_history_and_station(
        test_session,
        obs_tuple.network_name,
        obs_tuple.station_id,
        obs_tuple.lat,
        obs_tuple.lon,
    )
    assert history is not None

    q = test_session.query(Station)
    assert q.count() == 7

    q = test_session.query(History)
    assert q.count() == 9
    assert records_contain_db_connection(test_session, caplog)


def test_get_history_with_single_match(test_session, caplog):
    caplog.set_level(logging.DEBUG, "crmprtd")
    obs_tuple = Row(
        time=datetime.now(),
        val=123,
        variable_name="relative_humidity",
        unit="percent",
        network_name="MoTIe",
        station_id="11091",
        lat=None,
        lon=None,
    )

    history = find_or_create_matching_history_and_station(
        test_session,
        obs_tuple.network_name,
        obs_tuple.station_id,
        obs_tuple.lat,
        obs_tuple.lon,
    )
    assert history is not None

    q = test_session.query(Station)
    assert q.count() == 6

    q = test_session.query(History)
    assert q.count() == 8
    assert records_contain_db_connection(test_session, caplog)


def test_get_history_with_multiple_matches_and_location(test_session, caplog):
    caplog.set_level(logging.DEBUG, "crmprtd")
    obs_tuple = Row(
        time=datetime.now(),
        val=123,
        variable_name="relative_humidity",
        unit="percent",
        network_name="EC_raw",
        station_id="1047172",
        lat=49.45,
        lon=-123.7,
    )

    history = find_or_create_matching_history_and_station(
        test_session,
        obs_tuple.network_name,
        obs_tuple.station_id,
        obs_tuple.lat,
        obs_tuple.lon,
    )
    assert history.id == 20
    assert records_contain_db_connection(test_session, caplog)


def test_get_history_with_multiple_matches_and_no_location(test_session, caplog):
    caplog.set_level(logging.DEBUG, "crmprtd")
    obs_tuple = Row(
        time=datetime.now(),
        val=123,
        variable_name="relative_humidity",
        unit="percent",
        network_name="EC_raw",
        station_id="1047172",
        lat=None,
        lon=None,
    )

    history = find_or_create_matching_history_and_station(
        test_session,
        obs_tuple.network_name,
        obs_tuple.station_id,
        obs_tuple.lat,
        obs_tuple.lon,
    )
    assert history.id == 21
    assert records_contain_db_connection(test_session, caplog)


def test_get_variable(test_session):
    variable = get_variable(test_session, "FLNRO-WMB", "relative_humidity")
    assert variable.id == 3


def test_get_variable_no_match(test_session):
    variable = get_variable(test_session, "FLNRO-WMB", "humidity")
    assert variable is None


@pytest.mark.parametrize(
    ("network_name", "variable_name", "unit", "val", "expected"),
    [
        ("FLNRO-WMB", "relative_humidity", "percent", 10, 10),
        ("EC_raw", "precipitation", "cm", 10, 100),
    ],
)
def test_unit_check(test_session, network_name, variable_name, unit, val, expected):
    variable = get_variable(test_session, network_name, variable_name)
    check_val = convert_obs_value_to_db_units(val, unit, variable.unit)
    assert check_val == expected


@pytest.mark.parametrize(
    ("obs_tuple", "expected_hid", "expected_time", "expeceted_vid", "expected_datum"),
    [
        # use match_station_with_active to match
        (
            Row(
                time=datetime(2012, 9, 26, 18),
                val=123,
                variable_name="precipitation",
                unit="mm",
                network_name="EC_raw",
                station_id="1047172",
                lat=None,
                lon=None,
            ),
            21,
            datetime(2012, 9, 26, 18),
            2,
            123,
        ),
        # use unit_db_check to convert units
        (
            Row(
                time=datetime(2012, 9, 26, 18),
                val=10,
                variable_name="precipitation",
                unit="cm",
                network_name="EC_raw",
                station_id="1047172",
                lat=49.45,
                lon=-123.7,
            ),
            20,
            datetime(2012, 9, 26, 18),
            2,
            100,
        ),
        # get single match in get_history
        (
            Row(
                time=datetime(2012, 9, 26, 18),
                val=10,
                variable_name="CURRENT_AIR_TEMPERATURE1",
                unit="celsius",
                network_name="MoTIe",
                station_id="11091",
                lat=None,
                lon=None,
            ),
            1,
            datetime(2012, 9, 26, 18),
            1,
            10,
        ),
        # use create_station_and_history_entry for unrecognized station_id
        (
            Row(
                time=datetime(2012, 9, 26, 18),
                val=10,
                variable_name="CURRENT_AIR_TEMPERATURE1",
                unit="celsius",
                network_name="MoTIe",
                station_id="666",
                lat=49,
                lon=-121,
            ),
            5,
            datetime(2012, 9, 26, 18),
            1,
            10,
        ),
        # use match_station_with_location but no stations close enough
        (
            Row(
                time=datetime(2012, 9, 26, 18),
                val=123,
                variable_name="precipitation",
                unit="mm",
                network_name="EC_raw",
                station_id="1047172",
                lat=51,
                lon=-128,
            ),
            5,
            datetime(2012, 9, 26, 18),
            2,
            123,
        ),
    ],
)
def test_align_successes(
    test_session,
    obs_tuple,
    expected_hid,
    expected_time,
    expeceted_vid,
    expected_datum,
    caplog,
):
    caplog.set_level(logging.DEBUG, "crmprtd")
    ob = align(test_session, obs_tuple)
    assert ob.history_id == expected_hid
    assert ob.time == expected_time
    assert ob.vars_id == expeceted_vid
    assert ob.datum == expected_datum
    assert records_contain_db_connection(test_session, caplog)


@pytest.mark.parametrize(
    ("obs_tuple"),
    [
        # unit convertion failure
        (
            Row(
                time=datetime.now(),
                val=10,
                variable_name="CURRENT_AIR_TEMPERATURE1",
                unit="not_a_unit",
                network_name="MoTIe",
                station_id="11091",
                lat=None,
                lon=None,
            )
        ),
        # no unit in obs or db
        (
            Row(
                time=datetime.now(),
                val=10,
                variable_name="no_unit",
                unit=None,
                network_name="ENV-AQN",
                station_id="0260011",
                lat=None,
                lon=None,
            )
        ),
        # variable will not match any in db
        (
            Row(
                time=datetime.now(),
                val=10,
                variable_name="not_a_var",
                unit="celsius",
                network_name="MoTIe",
                station_id="11091",
                lat=None,
                lon=None,
            )
        ),
        # network does not exist
        (
            Row(
                time=datetime.now(),
                val=10,
                variable_name="CURRENT_AIR_TEMPERATURE1",
                unit="celsius",
                network_name="not_a_network",
                station_id="11091",
                lat=None,
                lon=None,
            )
        ),
        # missing vital information
        (
            Row(
                time=None,
                val=None,
                variable_name=None,
                unit="celsius",
                network_name="MoTIe",
                station_id="11091",
                lat=None,
                lon=None,
            )
        ),
        # no matching station and no way to create new station
        (
            Row(
                time=datetime.now(),
                val=15,
                variable_name="relative_humidity",
                unit="percent",
                network_name="FLNRO-WMB",
                station_id="1029",
                lat=None,
                lon=None,
            )
        ),
    ],
)
def test_align_failures(test_session, obs_tuple, caplog):
    caplog.set_level(logging.DEBUG, "crmprtd")
    ob = align(test_session, obs_tuple)
    assert ob is None
    assert records_contain_db_connection(test_session, caplog)


def test_closest_stns_within_threshold(ec_session):
    x = histories_within_threshold(ec_session, "EC_raw", -123.7, 49.45, 1000)
    assert len(x) > 0


def test_closest_stns_within_threshold_bad_data(ec_session):
    # https://github.com/pacificclimate/crmprtd/issues/8

    # Find some "good data" to use for the test run
    x, y = ec_session.query(ST_X(History.the_geom), ST_Y(History.the_geom)).first()

    # Create a couple history entries with reversed lat/lons
    space1 = History(
        station_name="Outer space", the_geom="SRID=4326;POINT(49.1658 -122.9606)"
    )
    space2 = History(
        station_name="Outer space", the_geom="SRID=4326;POINT(50.3225 122.7897)"
    )
    ec_session.add_all([space1, space2])
    ec_session.commit()

    # Just search for the good station and ensure there are not errors
    x = histories_within_threshold(ec_session, "EC_raw", x, y, 1)
    assert len(x) > 0


@pytest.mark.parametrize(
    ("alias", "dest"),
    (
        ("Deg.", "degree"),
        ("Deg", "degree"),
        ("\u00b0C", "celsius"),
        ("Celsius", "celsius"),
    ),
)
def test_convert_unit(alias, dest):
    x = 42
    assert convert_unit(x, alias, dest) == x
