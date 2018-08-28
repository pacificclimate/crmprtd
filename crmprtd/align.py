"""align.py

The align module handles the Align phase of the crmprtd pipeline. This
phase consists of performing database consistency checks required to
insert the incoming data records. Do the stations already exist or do
we need to create them? Do the variables exist or can we create them?
Etc. The input is a stream tuples and the output is a stream of
pycds.Obs objects. This phase is common to all networks.
"""

import logging
from pint import UnitRegistry, UndefinedUnitError

# local
from pycds import Obs, History, Network, Variable, Station
from crmprtd.db_exceptions import InsertionError


log = logging.getLogger(__name__)
ureg = UnitRegistry()
Q_ = ureg.Quantity


def closest_stns_within_threshold(sesh, network_name, lon, lat, threshold):
    query_txt = """
        WITH stns_in_thresh AS (
            SELECT history_id, station_id, lat, lon, Geography(ST_Transform(the_geom,4326)) as p_existing,
                Geography(ST_SetSRID(ST_MakePoint(:x, :y),4326)) as p_new
            FROM crmp.meta_history
            WHERE the_geom && ST_Buffer(Geography(ST_SetSRID(ST_MakePoint(:x, :y), 4326)),:thresh)
        )
        SELECT history_id, ST_Distance(p_existing,p_new) as dist
        FROM stns_in_thresh
        NATURAL JOIN crmp.meta_station
        NATURAL JOIN crmp.meta_network
        WHERE network_name = :network_name
        ORDER BY dist
""" # noqa
    q = sesh.execute(query_txt, {
        'x': lon,
        'y': lat,
        'thresh': threshold,
        'network_name': network_name}
    )
    valid_hid = set([x[0] for x in q.fetchall()])
    return valid_hid


def convert_unit(val, src_unit, dst_unit):
    if src_unit != dst_unit:
        try:
            val = Q_(val, ureg.parse_expression(src_unit))  # src
            val = val.to(dst_unit).magnitude  # dest
        except UndefinedUnitError as e:
            log.error('Unable to convert units',
                      extra={'src_unit': src_unit,
                             'dst_unit': dst_unit,
                             'exception': e})
            return None
    return val


def unit_check(val, unit_obs, unit_db):
    if unit_db is None:
        return None
    elif unit_obs is None:
        return val
    else:
        return convert_unit(val, unit_obs, unit_db)


def find_active_history(histories):
    matching_histories = [h for h in histories
                          if h.sdate is not None and h.edate is None]

    if len(matching_histories) == 1:
        hist = matching_histories.pop(0)
        log.debug('Matched history',
                  extra={'station_name': hist.station_name})
        return hist, False

    elif len(matching_histories) > 1:
        log.error('Multiple active stations in db',
                  extra={'num_active_stns': len(matching_histories),
                         'network_name': matching_histories[0].network_name})
        return None, False

    elif len(matching_histories) == 0:
        log.error('No active stations in db',
                  extra={'num_active_stns': len(matching_histories)})
        return None, False


def find_nearest_history(sesh, network_name, native_id, lat, lon, histories):
    close_stns = closest_stns_within_threshold(sesh, network_name,
                                               lon, lat, 800)

    if len(close_stns) == 0:
        return create_station_and_history_entry(sesh, network_name,
                                                native_id, lat, lon)

    for id in close_stns:
        for history in histories:
            if id == history.id:
                log.debug('Matched history',
                          extra={'station_name': history.station_name})
                return history, False


def match_station(sesh, network_name, native_id, lat, lon, histories):
    if lat and lon:
        return find_nearest_history(sesh, network_name, native_id,
                                    lat, lon, histories)
    else:
        return find_active_history(histories)


def create_station_and_history_entry(sesh, network_name, native_id, lat, lon):
    network = sesh.query(Network).filter(
        Network.name == network_name)

    network = network.first()
    stn = Station(native_id=native_id, network=network)

    log.info('Created new station entry',
             extra={'native_id': stn.native_id, 'network_name': network.name})

    hist = History(station=stn,
                   lat=lat,
                   lon=lon)

    log.warning('Created new history entry',
                extra={'history': hist.id, 'network_name': network_name,
                       'native_id': stn.native_id, 'lat': lat, 'lon': lon})
    try:
        sesh.add(stn)
        sesh.add(hist)
    except Exception as e:
        log.warning('Unable to insert new stn/hist entries',
                    extra={'stn': stn, 'hist': hist, 'exception': e})
        sesh.rollback()
        raise InsertionError(native_id=stn.id, hid=hist.id, e=e)
    else:
        sesh.commit()
    return hist, True


def get_variable(network_name, variable_name, variable_mapping):
    if variable_name in variable_mapping:
        return variable_mapping[variable_name]
    else:
        log.warning('Unable to match variable')
        return None


def get_history(sesh, network_name, native_id, lat, lon, history_mapping):
    """Returns a pycds history obj and an update boolean.  If a new history
       obj is created the history_mapping variable will need to be updated for
       next loop.
    """
    if native_id in history_mapping:
        histories = history_mapping[native_id]

        if len(histories) == 1:
            return next(iter(histories)), False
        elif len(histories) >= 2:
            return match_station(sesh, network_name, native_id, lat, lon,
                                 histories)
    else:
        return create_station_and_history_entry(sesh, network_name, native_id,
                                                lat, lon)


def is_network(network_mapping, network_name):
    if network_name in network_mapping:
        return True
    else:
        return False


def has_required_information(row_tuple):
    return row_tuple.network_name is not None and row_tuple.time is not None \
        and row_tuple.val is not None and row_tuple.variable_name is not None


def create_history_mapping(sesh, rows):
    '''Create a names -> history object map for the set of stations that are
       contained in the rows
    '''
    # Each row (observation) is attributed with a station
    # individually, so start by creating a set of unique stations in
    # the file. Minimize round-trips to the database.
    stn_ids = {row.station_id for row in rows}

    def lookup_stn(id):
        q = sesh.query(History).join(Station).join(Network)\
                .filter(Station.native_id == id)
        return q.all()
    mapping = [(id, lookup_stn(id)) for id in stn_ids]

    # Filter out ids for which we have no station metadata
    return {id: hist for id, hist in mapping if hist}


def create_variable_mapping(sesh, rows):
    '''Create a names -> history object map for the set of observations that are
       contained in the rows
    '''
    var_names = {(row.variable_name, row.network_name) for row in rows}

    def lookup_var(v, n):
        q = sesh.query(Variable).join(Network)\
                .filter(Network.name == n).filter(Variable.name == v)
        return q.first()
    mapping = [(var_name, lookup_var(var_name, net_name))
               for var_name, net_name in var_names]

    return {var_name: var_ for var_name, var_ in mapping if var_}


def create_network_mapping(sesh):
    q = sesh.query(Network)
    return {network.name: network for network in q.all()}


def align(sesh, rows):
    aligned = []
    history_mapping = create_history_mapping(sesh, rows)
    variable_mapping = create_variable_mapping(sesh, rows)
    network_mapping = create_network_mapping(sesh)

    for row_tuple in rows:
        # Without these items an Obs object cannot be produced
        if not has_required_information(row_tuple):
            log.warning('Observation missing critical information',
                        extra={'network_name': row_tuple.network_name,
                               'time': row_tuple.time,
                               'val': row_tuple.val,
                               'variable_name': row_tuple.variable_name})
            continue

        if not is_network(network_mapping, row_tuple.network_name):
            log.error('Network does not exist in db',
                      extra={'network_name': row_tuple.network_name})
            continue

        history, updated = get_history(sesh, row_tuple.network_name,
                                       row_tuple.station_id, row_tuple.lat,
                                       row_tuple.lon, history_mapping)

        if updated:
            history_mapping = create_history_mapping(sesh, rows)

        if not history:
            log.warning('Could not find history match',
                        extra={'network_name': row_tuple.network_name,
                               'native_id': row_tuple.station_id})
            continue

        variable = get_variable(row_tuple.network_name,
                                row_tuple.variable_name, variable_mapping)

        # Necessary attributes for Obs object
        if not variable:
            log.warning('Could not retrieve necessary information from db',
                        extra={'history': history, 'variable': variable})
            continue

        datum = unit_check(row_tuple.val, row_tuple.unit, variable.unit)
        if datum is None:
            log.warning('Unable to confirm data units',
                        extra={'unit_obs': row_tuple.unit,
                               'unit_db': variable.unit,
                               'data': row_tuple.val})
            continue

        # Note: We are very specifically creating the Obs object here using the
        # ids to avoid SQLAlchemy adding this object to the session as part of
        # its cascading backref behaviour https://goo.gl/Lchhv6
        aligned.append(Obs(history_id=history.id,
                           time=row_tuple.time,
                           datum=datum,
                           vars_id=variable.id))
    return aligned
