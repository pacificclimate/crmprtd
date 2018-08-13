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
from pint import UnitRegistry, UndefinedUnitError

# local
from pycds import Obs, History, Network, Variable, Station


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
    if src_unit != dst_unit and src_unit != None:
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
    if unit_obs == None and unit_db == None:
        return None
    else:
        val = convert_unit(val, unit_obs, unit_db)
        return val


def find_active_history(histories):
    matching_histories = [h for h in histories
                          if h.sdate is not None and h.edate is None]

    if len(matching_histories) == 1:
        hist = matching_histories.pop(0)
        log.debug('Matched history',
                  extra={'station_name': hist.station_name})
        return hist

    elif len(matching_histories) > 1:
        log.error('Multiple active stations in db',
                  extra={'num_active_stns': len(matching_histories),
                         'network_name': matching_histories[0].network_name})
        return None


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
                return history


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
    sesh.add(stn)
    log.info('Created new station entry',
             extra={'native_id': stn.native_id, 'network_name': network.name})

    hist = History(station=stn,
                   lat=lat,
                   lon=lon)

    sesh.add(hist)
    log.warning('Created new history entry',
                extra={'history': hist.id, 'network_name': network_name,
                       'native_id': stn.native_id, 'lat': lat, 'lon': lon})
    sesh.commit()
    return hist


def get_variable(sesh, network_name, variable_name):
    variable = sesh.query(Variable).join(Network).filter(and_(
        Network.name == network_name,
        Variable.name == variable_name)).first()

    if not variable:
        log.warning('Unable to match variable')
        return None

    return variable


def get_history(sesh, network_name, native_id, lat, lon):
    histories = sesh.query(History).join(Station).join(Network).filter(and_(
        Network.name == network_name,
        Station.native_id == native_id))

    if histories.count() == 0:
        return create_station_and_history_entry(sesh, network_name, native_id,
                                                lat, lon)
    elif histories.count() == 1:
        return histories.one_or_none()
    elif histories.count() >= 2:
        return match_station(sesh, network_name, native_id, lat, lon,
                             histories)


def is_network(sesh, network_name):
    network = sesh.query(Network).filter(
        Network.name == network_name)
    return network.count() != 0


def has_required_information(obs_tuple):
    return obs_tuple.network_name is not None and obs_tuple.time is not None \
        and obs_tuple.val is not None and obs_tuple.variable_name is not None


def align(sesh, obs_tuple):
    # Without these items an Obs object cannot be produced
    if not has_required_information(obs_tuple):
        log.warning('Observation missing critical information',
                    extra={'network_name': obs_tuple.network_name,
                           'time': obs_tuple.time,
                           'val': obs_tuple.val,
                           'variable_name': obs_tuple.variable_name})
        return None

    if not is_network(sesh, obs_tuple.network_name):
        log.error('Network does not exist in db',
                  extra={'network_name': obs_tuple.network_name})
        return None

    history = get_history(sesh, obs_tuple.network_name, obs_tuple.station_id,
                          obs_tuple.lat, obs_tuple.lon)
    if not history:
        log.warning('Could not find history match',
                    extra={'network_name': obs_tuple.network_name,
                           'native_id': obs_tuple.station_id})
        return None

    variable = get_variable(sesh, obs_tuple.network_name,
                            obs_tuple.variable_name)

    # Necessary attributes for Obs object
    if not variable:
        log.warning('Could not retrieve necessary information from db',
                    extra={'history': history, 'variable': variable})
        return None

    datum = unit_check(obs_tuple.val, obs_tuple.unit, variable.unit)
    if datum == None:
        log.warning('Unable to confirm data units',
                    extra={'unit_obs': obs_tuple.unit,
                           'unit_db': variable.unit,
                           'data': obs_tuple.val})
        return None

    return Obs(history=history,
               time=obs_tuple.time,
               datum=datum,
               variable=variable)
