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
from pint import UnitRegistry
import math

# local
from pycds import Obs, History, Network, Variable, Station
from crmprtd.ec import closest_stns_within_threshold


log = logging.getLogger(__name__)
ureg = UnitRegistry()
Q_ = ureg.Quantity


def create_station_and_history_entry(sesh, obs_tuple):
    network, = sesh.query(Network).filter(
        Network.name == obs_tuple.network_name).first()
    stn = Station(native_id=obs_tuple.native_id, network=obs_tuple.network)
    with sesh.begin_nested():
        sesh.add(stn)
    log.info('Created new station entry',
             extra={'station': stn, 'network': network,
                    'network_name': obs_tuple.network_name})

    hist = History(station=stn,
                   lat=obs_tuple.lat,
                   lon=obs_tuple.lon)

    with sesh.begin_nested():
        sesh.add(hist)
    log.info('Created new history entry',
             extra={'history': hist.id, 'network_name': obs_tuple.network_name,
                    'lat': obs_tuple.lat, 'lon': obs_tuple.lon})
    sesh.commit()
    return hist


def convert_unit(val, src_unit, dst_unit):
    try:
        val = Q_(val, ureg.parse_expression(src_unit))  # src
        val = val.to(dst_unit).magnitude  # dest
    except Exception:
        raise Exception(
            "Unable to convert source unit {} to destination unit {}".format(
                src_unit, dst_unit)
        )
    return val


def is_not_network(sesh, network_name):
    '''
    Check if given network name is not in the database
    '''
    network = sesh.query(Network).filter(Network.name == obs_tuple.network_name)
    return network.count() == 0


def get_history(sesh, obs_tuple):
    history = sesh.query(History).join(Station).join(Network).filter(and_(Network.name == obs_tuple.network_name, Station.native_id == obs_tuple.native_id))

    if history.count() == 0:
        return create_station_and_history_entry(sesh, obs_tuple)
    elif history.count() == 1:
        return history
    elif history.count() >= 2:
        return match_station(sesh, obs_tuple, history)
    else:
        return None


def match_station(sesh, obs_tuple, history):
    if lat and lon:
        return match_station_with_location(sesh, obs_tuple, history)
    else:
        return match_station_with_active(sesh, obs_tuple)


def match_station_with_location(sesh, obs_tuple, history):
    close_stns = closest_stns_within_threshold(sesh, lon, lat, 800)

    if len(close_stns) == 0:
        return create_station_and_history_entry(sesh, obs_tuple, history)

    for id in close_stns:
        for hist in history:
            if id == h.id:
                return hist

    # if we get here something has gone wrong
    return None


def match_station_with_active(sesh, obs_tuple, history):
    for id in history:
        hist = sesh.query(History).filter(
            and_(History.id == id,
                 History.sdate is not None,
                 History.edate is None))

        if hist:
            return hist

    # could not find a station
    return None


def get_variable(sesh, network_name, variable_name):
    variable = sesh.query(Variable).join(Network).filter(and_(
        Network.name == obs_tuple.network_name,
        Variable.name == obs_tuple.variable_name)).first()

    if not variable:
        return None

    return variable


def unit_check(sesh, unit_obs, unit_db, val):
    if not unit_obs and unit_db is None:
        return None
    else:
        return unit_db_check(unit_obs, unit_db, val)


def unit_db_check(unit_obs, unit_db, val):
    if unit_obs != unit_db:
        try:
            val_conv = convert_unit(val, unit_obs, unit_db)
        except Exception as e:
            log.error('Unable to convert units',
                      extra={'src_unit': unit,
                             'dst_unit': unit_db,
                             'exception': e})
            return None
        return val_conv
    else:
        return val


def align_refactor(sesh, obs_tuple):
    # Without these items an Obs object cannot be produced
    if not obs_tuple.network_name or not obs_tuple.time or not obs_tuple.val or not obs_tuple.variable_name:
        return None

    if is_not_network(sesh, obs_tuple.network_name):
        return None

    history = get_history(sesh, obs_tuple)
    variable = get_variable(sesh, obs_tuple.network_name, obs_tuple.variable_name)

    # Necessary attributes for Obs object
    if not history or not variable:
        return None

    datum = unit_check(sesh, variable, obs_tuple.unit, obs_tuple.val)
    if not datum:
        return None

    return Obs(history=history, time=time, datum=datum, variable=variable)


def align(sesh, obs_tuple):
    log.info('Begin alignment on row')

    # place
    log.debug('Check for network name')
    q = sesh.query(Network).filter(Network.name == obs_tuple.network_name)

    if q.count() == 0:
        log.error('Observation cannot be used without a valid network name',
                  extra={'network_name': obs_tuple.network_name})
        return
    log.debug('Found matching network name', extra={'network_name': q.first()})

    log.debug('Check if station id in history')
    q = sesh.query(History.id).join(Station).join(Network).filter(and_(
        Network.name == obs_tuple.network_name,
        Station.native_id == obs_tuple.station_id))

    hid = None
    if q.count() == 0:
        log.info('No station found, creating new station',
                 extra={'native_id': obs_tuple.station_id})
        hid = create_station_and_history_entry(sesh, obs_tuple)

    elif q.count() == 1:
        log.debug('Matched station', extra={'history_id': q.first()})
        hid, = q.first()

    # FIXME: What happens if we cannot find an "active" station?
    elif q.count() >= 2:
        log.debug('Found multiple stations', extra={
            'num_matches': q.count(), 'histories': q.all()})

        if obs_tuple.lat and obs_tuple.lon:
            matching_stns = []
            for hid in q.first():
                matching_stns.append(hid)
            matching_stns = set(matching_stns)
            close_stns = matching_stns.intersection(
                closest_stns_within_threshold(sesh, obs_tuple.lon,
                                              obs_tuple.lat, 800))
            log.debug('Station set intersection',
                      extra={'station_set': close_stns})

            if len(close_stns) == 0:
                log.debug('Station set is empty, adding new station')
                hid = create_station_and_history_entry(sesh, obs_tuple)

            elif len(close_stns) == 1:
                log.debug('Single station in set')
                hid = close_stns.pop()

            elif len(close_stns) > 1:
                log.debug('Multiple stations in set')
                closest_pos = 999   # max distance should be 800m at this point
                for id in close_stns:
                    try:
                        lat, lon = sesh.query(History.lat, History.lon).filter(
                            History.id == id).first()
                    except Exception as e:
                        log.warning('An error occured while accesing the db',
                                    extra={'exception': e})

                    dist = haversine_formula(obs_tuple.lat,
                                             obs_tuple.lon,
                                             float(lat),
                                             float(lon))

                    # best case, we find exact match
                    if dist == 0:
                        log.debug('Exact match found')
                        hid = id
                        break

                    # find closest
                    else:
                        if dist < closest_pos:
                            hid = id
                            closest_pos = dist

            if not hid:
                log.debug('Observation contains lat/lon but does not match '
                          'any entries in db')
                hid = create_station_and_history_entry(sesh, obs_tuple)
        else:
            log.debug('No lat/lon, checking for \"active\" stations')
            for id in q.all():
                q = sesh.query(History.id).filter(
                    and_(History.id == id,
                         History.sdate is not None,
                         History.edate is None))

                if q.count() > 0:
                    log.debug('Matched hid using sdate/edate')
                    hid, = q.first()
                    break

        if not hid:
            log.warning('Unable to match station',
                        extra={'station_id': obs_tuple.station_id,
                               'network_name': obs_tuple.network_name})
            return

    # thing
    log.debug('Check time')
    if obs_tuple.time is None:
        log.error('Observation cannot be used without time')
        return
    log.debug('Observation has time')
    time = obs_tuple.time

    log.debug('Check data')
    if obs_tuple.val is None:
        log.error('Observation cannot be used without value')
        return
    log.debug('Observation has value')
    datum = obs_tuple.val

    log.debug('Check if variable name exists in database')
    q = sesh.query(Variable.id).join(Network).filter(and_(
        Network.name == obs_tuple.network_name,
        Variable.name == obs_tuple.variable_name))

    if q.count() < 1:
        log.warning('No matching variable found', extra={
                    'vars_id': obs_tuple.variable_name})
        return

    vars_id, = q.first()
    log.debug('Observation variable matches', extra={'vars_id': vars_id})

    log.debug('Check unit')
    if obs_tuple.unit is None:
        log.debug('No unit given, checking if table contains unit')
        unit, = sesh.query(Variable.unit).join(Network).filter(and_(
            Network.name == obs_tuple.network_name,
            Variable.name == obs_tuple.variable_name)).first()

        if not unit:
            log.warning('Table contains no unit for variable',
                        extra={'var_name': obs_tuple.variable_name})
            return
        log.debug('Unit found')

    else:
        log.debug('Observation has unit, check if it matches db')
        unit = obs_tuple.unit
        unit_db, = sesh.query(Variable.unit).join(Network).filter(and_(
            Network.name == obs_tuple.network_name,
            Variable.name == obs_tuple.variable_name)).first()

        if unit_db != unit:
            log.debug('Units do not match, converting')

            try:
                datum = convert_unit(datum, unit, unit_db)
            except Exception as e:
                log.error('Unable to convert units',
                          extra={'src_unit': unit,
                                 'dst_unit': unit_db,
                                 'exception': e})
                return
            log.debug('Unit converted', extra={
                     'src_unit': unit, 'dst_unit': unit_db})
        else:
            log.debug('Units match')

    log.info('Alignment completed')
    return Obs(time=time, vars_id=vars_id, history_id=hid, datum=datum)
