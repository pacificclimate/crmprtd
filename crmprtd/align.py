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
    # FIXME: add more to extra
    network_id, = sesh.query(Network.id).filter(
        Network.name == obs_tuple.network_name).first()
    stn = Station(native_id=obs_tuple.station_id, network_id=network_id)
    with sesh.begin_nested():
        sesh.add(stn)
    log.info('Created new station_id', extra={'stationd_id': stn.id})

    if obs_tuple.lat and obs_tuple.lon:
        hist = History(station=stn,
                       lat=obs_tuple.lat,
                       lon=obs_tuple.lon)
    else:
        hist = History(station=stn)

    with sesh.begin_nested():
        sesh.add(hist)
    log.info('Created new history entry', extra={'history': hist.id})
    sesh.commit()
    return hist.id


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


def haversine_formula(lat1, lon1, lat2, lon2):
    R = 6378.137
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000


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

    if q.count() == 0:
        log.info('No station found, creating new station',
                 extra={'native_id': obs_tuple.station_id})
        hid = create_station_and_history_entry(sesh, obs_tuple)

    elif q.count() == 1:
        log.debug('Matched station', extra={'history_id': q.first()})
        hid, = q.first()

    elif q.count() >= 2:    # FIXME: This needs to be handled in some way
        log.info('Found multiple stations', extra={
            'num_matches': q.count(), 'histories': q.all()})
        hid = None
        if obs_tuple.lat and obs_tuple.lon:
            matching_stns = []
            for hid in q.first():
                matching_stns.append(hid)
            matching_stns = set(matching_stns)
            close_stns = matching_stns.intersection(closest_stns_within_threshold(sesh, obs_tuple.lon, obs_tuple.lat, 800))
            log.info('Station set intersection', extra={'station_set': close_stns})

            if len(close_stns) == 0:
                hid = create_station_and_history_entry(sesh, obs_tuple)

            elif len(close_stns) == 1:
                hid = close_stns.pop()

            elif len(close_stns) > 1:
                closest_pos = 999   # max distance should be 800m at this point
                for id in close_stns:
                    try:
                        lat, lon = sesh.query(History.lat, History.lon).filter(
                                    History.id == id).first()
                    except Exception:
                        log.warning('Could not unpack values')

                    dist = haversine_formula(obs_tuple.lat, obs_tuple.lon, float(lat), float(lon))
                    # best case, we find exact match
                    if dist == 0:
                        log.info('Exact match found')
                        hid = id
                        break

                    # find closest
                    else:
                        if dist < closest_pos:
                            hid = id
                            closest_pos = dist

            if not hid:
                hid = create_station_and_history_entry(sesh, obs_tuple)
        else:
            for id in q.all():
                q = sesh.query(History.id).filter(
                    and_(History.id == id,
                         History.sdate is not None,
                         History.edate is None))

                if q.count() > 0:
                    log.info('Matched hid using sdate/edate')
                    hid, = q.first()
                    break

        if not hid:
            log.error('Unable to match station')
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

    log.info('Check unit')
    if obs_tuple.unit is None:
        log.info('No unit given, checking if table contains unit')
        unit, = sesh.query(Variable.unit).join(Network).filter(and_(
            Network.name == obs_tuple.network_name,
            Variable.name == obs_tuple.variable_name)).first()
        if not unit:
            log.info('Table contains no unit for variable',
                     extra={'var_name': obs_tuple.variable_name})
            return
        log.info('Unit found')
    else:
        log.info('Observation has unit, check if it matches db')
        unit = obs_tuple.unit
        unit_db, = sesh.query(Variable.unit).join(Network).filter(and_(
            Network.name == obs_tuple.network_name,
            Variable.name == obs_tuple.variable_name)).first()

        if unit_db != unit:
            log.info('Units do not match, converting')
            # converting
            try:
                datum = convert_unit(datum, unit, unit_db)
            except Exception as e:
                log.error('Unable to convert units',
                          extra={'src_unit': unit,
                                 'dst_unit': unit_db,
                                 'exception': e})
                return
            log.info('Unit converted', extra={
                     'src_unit': unit, 'dst_unit': unit_db})
        else:
            log.info('Units match')

    log.info('Alignment completed')
    yield Obs(time=time, vars_id=vars_id, history_id=hid, datum=datum)
