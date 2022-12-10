"""align.py

The align module handles the Align phase of the crmprtd pipeline. This
phase consists of performing database consistency checks required to
insert the incoming data records. Do the stations already exist or do
we need to create them? Do the variables exist or can we create them?
Etc. The input is a stream tuples and the output is a stream of
pycds.Obs objects. This phase is common to all networks.
"""

import logging
from sqlalchemy import and_
from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

# local
from pycds import Obs, History, Network, Variable, Station
from crmprtd.db_exceptions import InsertionError


log = logging.getLogger(__name__)
ureg = UnitRegistry()
Q_ = ureg.Quantity
# These definitions have been added (https://git.io/Je9RB) since the
# latest release of pint (0.9). This can be removed once we incorporate pint's
# next release.
for def_ in (
    "degreeC = degC; offset: 273.15 = °C = celsius = Celsius",
    "degreeF = 5 / 9 * kelvin; offset: 255.372222",
    "degreeK = degK; offset: 0",
    "degree = π / 180 * radian = deg = Deg = arcdeg = arcdegree = " "angular_degree",
):
    ureg.define(def_)


def history_ids_within_threshold(sesh, network_name, lon, lat, threshold):
    """
    Return a set containing the id's of existing histories associated with the
    given network and within a threshold distance of the lat and lon.

    :param sesh: SQLAlchemy db session
    :param network_name: Name of network associated to history.
    :param lat: Lat for History
    :param lon: Lon for History
    :param threshold: Include only histories within this distance from (lat, lon)
    :return: Set of history ids.
    """

    query_txt = """
        WITH hxs_in_thresh AS (
            SELECT 
                history_id, 
                station_id, 
                lat, 
                lon, 
                Geography(ST_Transform(the_geom, 4326)) as p_existing,
                Geography(ST_SetSRID(ST_MakePoint(:x, :y), 4326)) as p_new
            FROM crmp.meta_history
            WHERE the_geom && ST_Buffer(
                Geography(ST_SetSRID(ST_MakePoint(:x, :y), 4326)), :thresh
            )
        )
        SELECT 
            history_id, ST_Distance(p_existing, p_new) as dist
        FROM hxs_in_thresh hx
        JOIN crmp.meta_station stn ON (hx.station_id = stn.station_id)
        JOIN crmp.meta_network nw ON (stn.network_id = nw.network_id)
        WHERE nw.network_name = :network_name
        ORDER BY dist
"""  # noqa
    # TODO: Why is dist computed and rows ordered by it if the result is unordered??
    q = sesh.execute(
        query_txt,
        {"x": lon, "y": lat, "thresh": threshold, "network_name": network_name},
    )
    valid_hid = set([x[0] for x in q.fetchall()])
    return valid_hid


def convert_unit(val, src_unit, dst_unit):
    if src_unit != dst_unit:
        try:
            val = Q_(val, ureg.parse_expression(src_unit))  # src
            val = val.to(dst_unit).magnitude  # dest
        except (UndefinedUnitError, DimensionalityError) as e:
            log.error(
                "Unable to convert units",
                extra={"src_unit": src_unit, "dst_unit": dst_unit, "exception": e},
            )
            return None
    return val


def convert_obs_value_to_db_units(val, unit_obs, unit_db):
    """
    Convert observation data value to database units, if possible.

    :param val: Data value
    :param unit_obs: Observation unit; assume database unit if absent
    :param unit_db: Database unit
    :return: value or None
    """
    if unit_db is None:
        return None
    elif unit_obs is None:
        return val
    else:
        return convert_unit(val, unit_obs, unit_db)


def find_active_history(histories):
    matching_histories = [
        h for h in histories if h.sdate is not None and h.edate is None
    ]

    if len(matching_histories) == 1:
        hist = matching_histories.pop(0)
        log.debug("Matched history", extra={"station_name": hist.station_name})
        return hist

    elif len(matching_histories) > 1:
        log.error(
            "Multiple active stations in db",
            extra={
                "num_active_stns": len(matching_histories),
                "network_name": matching_histories[0].network_name,
            },
        )
        return None


def find_nearest_history(
    sesh, network_name, native_id, lat, lon, histories, diagnostic=False
):
    close_stns = history_ids_within_threshold(sesh, network_name, lon, lat, 800)

    if len(close_stns) == 0:
        return create_station_and_history_entry(
            sesh, network_name, native_id, lat, lon, diagnostic=diagnostic
        )

    for id in close_stns:
        for history in histories:
            if id == history.id:
                log.debug(
                    "Matched history", extra={"station_name": history.station_name}
                )
                return history


def match_history(sesh, network_name, native_id, lat, lon, histories, diagnostic=False):
    if lat and lon:
        return find_nearest_history(
            sesh, network_name, native_id, lat, lon, histories, diagnostic=diagnostic
        )
    else:
        return find_active_history(histories)


def create_station_and_history_entry(
    sesh, network_name, native_id, lat, lon, diagnostic=False
):
    """
    Create a Station and an associated History object according to the arguments.

    :param sesh: SQLAlchemy db session
    :param network_name: Name of network associated to Station.
    :param native_id: Native id of Station.
    :param lat: Lat for History
    :param lon: Lon for History
    :param diagnostic: Boolean. In diagnostic mode? Not used!
    :return: None
    """
    network = sesh.query(Network).filter(Network.name == network_name).first()

    action = "Requires" if diagnostic else "Created"

    station = Station(native_id=native_id, network_id=network.id)
    log.info(
        f"{action} new station entry",
        extra={"native_id": station.native_id, "network_name": network.name},
    )

    history = History(station=station, lat=lat, lon=lon)
    log.warning(
        f"{action} new history entry",
        extra={
            "history": history.id,
            "network_name": network_name,
            "native_id": station.native_id,
            "lat": lat,
            "lon": lon,
        },
    )

    if diagnostic:
        return None

    try:
        sesh.add(station)
        sesh.add(history)
    except Exception as e:
        log.warning(
            "Unable to insert new stn/hist entries",
            extra={"stn": station, "hist": history, "exception": e},
        )
        sesh.rollback()
        raise InsertionError(native_id=station.id, hid=history.id, e=e)
    else:
        sesh.commit()

    return history


def get_variable(sesh, network_name, variable_name):
    """
    Find (but not create) a Variable matching the arguments, if possible.

    :param sesh: SQLAlchemy db session
    :param network_name: Name of network that Variable must be in.
    :param variable_name: Name of Variable
    :return: Variable or None
    """
    variable = (
        sesh.query(Variable)
        .join(Network)
        .filter(and_(Network.name == network_name, Variable.name == variable_name))
        .first()
    )
    return variable


def find_or_create_matching_history_and_station(
    sesh, network_name, native_id, lat, lon, diagnostic=False
):
    """
    Find or create a History and associated Station record matching the arguments,
    if possible.

    Always return a matching History if it already exists in the database.

    In diagnostic mode, do not create any new records (History or Station).

    :param sesh: SQLAlchemy db session
    :param network_name: Name of network that History must be in.
    :param native_id: Native id of station that history must be associated with.
    :param lat: Lat for history record; either for spatial matching or creation -
        see below
    :param lon: Lon for history record; either for spatial matching or creation -
        see below
    :param diagnostic: Boolean. In diagnostic mode?
    :return: History object or None

    Search db for existing history records exactly matching network_name and station_id.

    If no such history is found, create one (along with the necessary station record)
    and return it. In diagnostic mode, do not create new records.

    If exactly one such history is found, return it.

    If more than one such history is found, do a spatial (lat, lon) match on them.
    - If at least one is found within tolerance distance, return one.
    - If none are found within tolerance, this is an error condition, return None.
    """
    log.debug("Searching for native_id = %s", native_id)
    histories = (
        sesh.query(History)
        .join(Station)
        .join(Network)
        .filter(and_(Network.name == network_name, Station.native_id == native_id))
    )

    if histories.count() == 0:
        log.debug("Cound not find native_id %s", native_id)
        if diagnostic:
            log.info(
                f"In diagnostic mode. Skipping insertion of new history entry: {network_name}, {native_id}, {lat}, {lon}"
            )
            return None
        return create_station_and_history_entry(sesh, network_name, native_id, lat, lon)
    elif histories.count() == 1:
        log.debug("Found exactly one matching history_id")
        return histories.one_or_none()
    elif histories.count() >= 2:
        log.debug("Found multiple history entries. Searching for match.")
        return match_history(
            sesh, network_name, native_id, lat, lon, histories, diagnostic=diagnostic
        )


def does_network_exist(sesh, network_name):
    network = sesh.query(Network).filter(Network.name == network_name)
    return network.count() != 0


def has_required_information(obs_tuple):
    return (
        obs_tuple.network_name is not None
        and obs_tuple.time is not None
        and obs_tuple.val is not None
        and obs_tuple.variable_name is not None
    )


def align(sesh, obs_tuple, diagnostic=False):
    """
    Create, if possible, an Obs object from the obs_tuple and return it.

    :param sesh: SQLAlchemy db session
    :param obs_tuple: Single record from input data defining an observation.
    :param diagnostic: Boolean. In diagnostic mode?
    :return: Obs or None

    Steps:
    1. Do data sanity checks. On fail, return None.
    2. Find or create matching history and station records. If not possible, return None.
        In diagnostic mode, do not create new records; return None.
    3. Convert observation value to database units. If not possible, return None.
    4. Create Obs using history, network, value, and return it.
    """

    # Sanity check: obs tuple contains all info required to create an Obs object
    if not has_required_information(obs_tuple):
        log.debug(
            "Observation missing critical information",
            extra={
                "network_name": obs_tuple.network_name,
                "time": obs_tuple.time,
                "val": obs_tuple.val,
                "variable_name": obs_tuple.variable_name,
            },
        )
        return None

    # Sanity check: specified network exists
    if not does_network_exist(sesh, obs_tuple.network_name):
        log.error(
            "Network does not exist in db",
            extra={"network_name": obs_tuple.network_name},
        )
        return None

    # Find or create a matching History record, if possible.
    history = find_or_create_matching_history_and_station(
        sesh,
        obs_tuple.network_name,
        obs_tuple.station_id,
        obs_tuple.lat,
        obs_tuple.lon,
        diagnostic,
    )
    if not history:
        log.warning(
            "Could not find history match",
            extra={
                "network_name": obs_tuple.network_name,
                "native_id": obs_tuple.station_id,
            },
        )
        return None

    # Find a matching Variable object, if possible.
    variable = get_variable(sesh, obs_tuple.network_name, obs_tuple.variable_name)
    if not variable:
        log.debug(
            'Variable "%s" from network "%s" is not tracked by crmp',
            obs_tuple.variable_name,
            obs_tuple.network_name,
        )
        return None

    # Convert observation value to database units.
    datum = convert_obs_value_to_db_units(obs_tuple.val, obs_tuple.unit, variable.unit)
    if datum is None:
        log.debug(
            "Unable to confirm data units",
            extra={
                "unit_obs": obs_tuple.unit,
                "unit_db": variable.unit,
                "data": obs_tuple.val,
                "network_name": obs_tuple.network_name,
            },
        )
        return None

    # Create Obs object.
    # Note: We are very specifically creating the Obs object here using the ids
    # to avoid SQLAlchemy adding this object to the session as part of its
    # cascading backref behaviour https://goo.gl/Lchhv6
    return Obs(
        history_id=history.id, time=obs_tuple.time, datum=datum, vars_id=variable.id
    )
