"""align.py

The align module handles the Align phase of the crmprtd pipeline. This
phase consists of performing database consistency checks required to
insert the incoming data records. Do the stations already exist or do
we need to create them? Do the variables exist or can we create them?
Etc. The input is a stream tuples and the output is a stream of
pycds.Obs objects. This phase is common to all networks.
"""

import logging
from types import SimpleNamespace

from sqlalchemy import and_, cast
from geoalchemy2.functions import (
    ST_Buffer,
    ST_Distance,
    ST_Transform,
    ST_SetSRID,
    ST_MakePoint,
)
from geoalchemy2.types import Geography
from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

from pycds import Obs, History, Network, Variable, Station
from crmprtd.db_exceptions import InsertionError
from crmprtd.log_helpers import sanitize_connection

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
    "degree = π / 180 * radian = deg = Deg = arcdeg = arcdegree = angular_degree",
):
    ureg.define(def_)


def cached_function(attrs):
    """A decorator factory that can be used to cache database results

    Neither database sessions (i.e. the sesh parameter of each wrapped
    function) nor SQLAlchemy mapped objects (the results of queries) are
    cachable or reusable. Therefore one cannot memoize database query
    functions using builtin things like the lrucache.

    This wrapper works, by a) assuming that the wrapped function's first
    argument is a database session b) assuming that the result of the
    query returns a single SQLAlchemy object (e.g. a History instance),
    and c) accepting as a parameter a list of attributes to retrieve and
    store in the cache result.

    args (except sesh) and kwargs to the wrapped function are used as
    the cache key, and results are the parametrized object attributes.
    """

    def wrapper(f):
        cache = {}

        def memoize(sesh, *args, **kwargs):
            nonlocal cache
            key = (args) + tuple(kwargs.items())
            if key not in cache:
                obj = f(sesh, *args, **kwargs)
                log.debug(
                    f"Cache miss: {f.__name__} {key} -> {repr(obj)}",
                    extra={"database": sanitize_connection(sesh)},
                )
                cache[key] = obj and SimpleNamespace(
                    **{attr: getattr(obj, attr) for attr in attrs}
                )
            return cache[key]

        return memoize

    return wrapper


def histories_within_threshold(sesh, network_name, lon, lat, threshold):
    """
    Find existing histories associated with the given network and within a threshold
    distance of the point specified by (lon, lat). Return the history id and distance
    for each such history, as a list in ascending order of distance.

    :param sesh: SQLAlchemy db session
    :param network_name: Name of network associated to history.
    :param lat: Lat for History
    :param lon: Lon for History
    :param threshold: Include only histories within this distance (m) from (lat, lon)
    :return: List of records with attributes history_id, distance, in ascending order
        of distance.
    """

    # Construct reference point at (lon, lat) for distance computations.
    p_ref = cast(ST_SetSRID(ST_MakePoint(lon, lat), 4326), Geography)

    # Histories in network AND within threshold distance of (lon, lat).
    hxs_within_threshold = (
        sesh.query(
            History.id.label("history_id"),
            History.station_id.label("station_id"),
            cast(ST_Transform(History.the_geom, 4326), Geography).label("p_this"),
            p_ref.label("p_ref"),
        )
        .select_from(History)
        .join(Station, History.station_id == Station.id)
        .join(Network, Station.network_id == Network.id)
        .filter(Network.name == network_name)
        .filter(
            History.the_geom.intersects(ST_Buffer(p_ref, threshold)),
        )
        .cte(name="hxs_in_thresh")
    )

    # Result set of those histories (id's), with distance from (lon, lat).
    hxs_by_distance = list(
        sesh.query(
            hxs_within_threshold.c.history_id.label("history_id"),
            ST_Distance(
                hxs_within_threshold.c.p_this, hxs_within_threshold.c.p_ref
            ).label("distance"),
        )
        .select_from(hxs_within_threshold)
        .order_by("distance")
        .all()
    )

    return hxs_by_distance


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
    close_histories = histories_within_threshold(sesh, network_name, lon, lat, 800)

    if len(close_histories) == 0:
        return create_station_and_history_entry(
            sesh, network_name, native_id, lat, lon, diagnostic=diagnostic
        )

    for close_history in close_histories:
        for history in histories:
            if close_history.history_id == history.id:
                log.debug(
                    "Matched history",
                    extra={
                        "station_name": history.station_name,
                        "database": sanitize_connection(sesh),
                    },
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
        extra={
            "native_id": station.native_id,
            "network_name": network.name,
            "database": sanitize_connection(sesh),
        },
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
            "database": sanitize_connection(sesh),
        },
    )

    if diagnostic:
        log.info(
            f"In diagnostic mode. Skipping insertion of new history entry for: "
            f"network_name={network_name}, native_id={native_id}, lat={lat}, lon={lon}",
            extra={"database": sanitize_connection(sesh)},
        )
        return None

    try:
        with sesh.begin_nested():
            sesh.add(station)
            sesh.add(history)
    except Exception as e:
        log.warning(
            "Unable to insert new stn/hist entries",
            extra={
                "stn": station,
                "hist": history,
                "exception": e,
                "database": sanitize_connection(sesh),
            },
        )
        raise InsertionError(native_id=station.id, hid=history.id, e=e)
    sesh.commit()

    return history


@cached_function(["unit", "id"])
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


@cached_function(["id"])
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
    log.debug(
        "Searching for native_id = %s",
        native_id,
        extra={"database": sanitize_connection(sesh)},
    )
    histories = (
        sesh.query(History)
        .join(Station)
        .join(Network)
        .filter(and_(Network.name == network_name, Station.native_id == native_id))
    )

    if histories.count() == 0:
        log.debug(
            "Cound not find native_id %s",
            native_id,
            extra={"database": sanitize_connection(sesh)},
        )
        return create_station_and_history_entry(
            sesh, network_name, native_id, lat, lon, diagnostic=diagnostic
        )
    elif histories.count() == 1:
        log.debug(
            "Found exactly one matching history_id",
            extra={"database": sanitize_connection(sesh)},
        )
        return histories.one_or_none()
    elif histories.count() >= 2:
        log.debug(
            "Found multiple history entries. Searching for match.",
            extra={"database": sanitize_connection(sesh)},
        )
        return match_history(
            sesh, network_name, native_id, lat, lon, histories, diagnostic=diagnostic
        )


@cached_function(["name"])
def get_network(sesh, network_name):
    return sesh.query(Network).filter(Network.name == network_name).first()


def has_required_information(row):
    return (
        row.network_name is not None
        and row.time is not None
        and row.val is not None
        and row.variable_name is not None
    )


def align(sesh, row, diagnostic=False):
    """
    Create, if possible, an Obs object from the obs_tuple and return it.

    :param sesh: SQLAlchemy db session
    :param row: Single Row defining an observation.
    :param diagnostic: Boolean. In diagnostic mode?
    :return: Obs or None

    Steps:
    1. Do data sanity checks. On fail, return None.
    2. Find or create matching history and station records. If not possible,
        return None. In diagnostic mode, do not create new records; return None.
    3. Convert observation value to database units. If not possible, return None.
    4. Create Obs using history, network, value, and return it.
    """

    # Sanity check: row contains all info required to create an Obs object
    if not has_required_information(row):
        log.debug(
            "Observation missing critical information",
            extra={
                "network_name": row.network_name,
                "time": row.time,
                "val": row.val,
                "variable_name": row.variable_name,
                "database": sanitize_connection(sesh),
            },
        )
        return None

    # Sanity check: specified network exists
    if not get_network(sesh, row.network_name):
        log.error(
            "Network does not exist in db",
            extra={
                "network_name": row.network_name,
                "database": sanitize_connection(sesh),
            },
        )
        return None

    # Find or create a matching History record, if possible.
    history = find_or_create_matching_history_and_station(
        sesh,
        row.network_name,
        row.station_id,
        row.lat,
        row.lon,
        diagnostic,
    )
    if not history:
        log.warning(
            "Could not find history match",
            extra={
                "network_name": row.network_name,
                "native_id": row.station_id,
                "database": sanitize_connection(sesh),
            },
        )
        return None

    # Find a matching Variable object, if possible.
    variable = get_variable(sesh, row.network_name, row.variable_name)
    if not variable:
        log.debug(
            'Variable "%s" from network "%s" is not tracked by crmp',
            row.variable_name,
            row.network_name,
            extra={"database": sanitize_connection(sesh)},
        )
        return None
    else:
        var_unit = variable.unit
        var_id = variable.id

    # Convert observation value to database units.
    datum = convert_obs_value_to_db_units(row.val, row.unit, var_unit)
    if datum is None:
        log.debug(
            "Unable to confirm data units",
            extra={
                "unit_obs": row.unit,
                "unit_db": var_unit,
                "data": row.val,
                "network_name": row.network_name,
                "database": sanitize_connection(sesh),
            },
        )
        return None

    # Create Obs object.
    # Note: We are very specifically creating the Obs object here using the ids
    # to avoid SQLAlchemy adding this object to the session as part of its
    # cascading backref behaviour https://goo.gl/Lchhv6
    return Obs(history_id=history.id, time=row.time, datum=datum, vars_id=var_id)
