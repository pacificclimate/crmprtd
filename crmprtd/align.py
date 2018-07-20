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
import re

# local
from pycds import Obs, History, Network, Variable, Station


log = logging.getLogger(__name__)
ureg = UnitRegistry()
Q_ = ureg.Quantity


def create_station_and_history_entry(sesh, obs_tuple, network_id):
    stn = Station(native_id=obs_tuple.station_id, network_id=network_id)
    with sesh.begin_nested():
        sesh.add(stn)
    log.info('Created new station_id', extra={'stationd_id': stn.id})

    # FIXME: Need a way to have station name attribute
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
            "Can't convert source unit {} to destination unit {}".format(
                src_unit, dst_unit)
        )


def align(sesh, obs_tuple):
    # place (network name, station id)
    log.info('Begin alignment on row')

    log.debug('Check for network name')
    q = sesh.query(Network).filter(Network.name == obs_tuple.network_name)

    if q.count() == 0:
        log.error('Observation cannot be used without a valid network name', extra={'network_name': obs_tuple.network_name})
        return
    log.debug('Found matching network name', extra={'network_name': q.first()})

    log.debug('Check if station id in history')
    q = sesh.query(History.id).join(Station).join(Network).filter(and_(Network.name == obs_tuple.network_name, Station.native_id == obs_tuple.station_id))

    if q.count() == 0:
        log.info('No station found, creating new station', extra={'native_id': obs_tuple.station_id})
        network_id, = sesh.query(Network.id).filter(Network.name == obs_tuple.network_name).first()
        hid = create_station_and_history_entry(sesh, obs_tuple, network_id)

    elif q.count() == 1:
        log.debug('Matched station', extra={'history_id': q.first()})
        hid, = q.first()

    elif q.count() >= 2:    # FIXME: This needs to be handled in some way
        log.debug('Found multiple stations', extra={'num_matches': q.count(), 'histories': q.all()})
        hid = None
        if obs_tuple.lat and obs_tuple.lon:
            for id in q.all():
                lat, lon = sesh.query(History.lat, History.lon).filter(History.id == id)

                if lat == obs_tuple.lat and lon == obs_tuple.lon:
                    log.info('Matched hid using lat/lon')
                    hid = id
                    break
        else:
            for id in q.all():
                q = sesh.query(History.id).filter(and_(History.id == id, History.sdate is not NULL, History.edate is NULL))

                if q.count() > 0:
                    log.info('Matched hid using sdate/edate')
                    hid, = q.first()
                    break

        if not hid:
            log.error('Unable to match station')
            return

    # thing (val, variable name, unit)
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
    q = sesh.query(Variable.id).join(Network).filter(and_(Network.name == obs_tuple.network_name, Variable.name == obs_tuple.variable_name))

    if q.count() < 1:
        log.warning('No matching variable found', extra={'vars_id': obs_tuple.variable_name})
        return

    vars_id, = q.first()
    log.debug('Observation variable matches', extra={'vars_id': vars_id})

    log.info('Check unit')
    if obs_tuple.unit is None:
        log.info('No unit given, checking if table contains unit')
        unit, = sesh.query(Variable.unit).join(Network).filter(Network.name == obs_tuple.network_name).filter(Variable.name == obs_tuple.variable_name).first()
        if not unit:
            log.info('Table contains no unit for variable', extra={'var_name': obs_tuple.variable_name})
            return
        log.info('Unit found')
    else:
        log.info('Observation has unit, check if it matches db')
        unit = obs_tuple.unit
        unit_db, = sesh.query(Variable.unit).join(Network).filter(Network.name == obs_tuple.network_name).filter(Variable.name == obs_tuple.variable_name).first()

        if unit_db != unit:
            log.info('Units do not match, converting')
            # converting
            try:
                datum = convert_unit(datum, unit, unit_db)
            except Exception as e:
                log.error('Unable to convert units', extra={'src_unit': unit, 'dst_unit': unit_db, 'exception': e})
                return
            log.info('Unit converted', extra={'src_unit': unit, 'dst_unit': unit_db})
        else:
            log.info('Units match')

    log.info('Alignment completed')
    yield Obs(time=time, vars_id=vars_id, history_id=hid, datum=datum)
