from pkg_resources import resource_filename
from datetime import datetime, timedelta
import logging

import pytz
from lxml.etree import parse, XSLT
from sqlalchemy.exc import IntegrityError

from pycds import History, Network, Station, Variable, Obs


log = logging.getLogger(__name__)

xsl = resource_filename('crmprtd', 'data/moti.xsl')
transform = XSLT(parse(xsl))

ns = {
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

unwanted_vars = [
    ('pavement', 'temperature', 'celsius'),
    ('pavement', 'freeze-point', 'celsius'),
    ('pavement', 'surface-status', 'code'),
    ('subsurface', 'temperature', 'celsius'),
    ('extension', None, 'unitless')
]


def makeurl(report='7110', request='historic',
            station=None, from_=None, to=None):
    '''
    Construct a URL for fetching the data file
    '''
    fmt = '%Y-%m-%d/%H'
    from_ = from_.strftime(fmt)
    to = to.strftime(fmt)
    url = ('https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr{report}?'
           'request={request}&station={station}&from={from_}'
           '&to={to}').format(**locals())
    return url


def process(sesh, et):
    et = transform(et)

    obs_series = et.xpath("//observation-series")
    successes, failures, skips = 0, 0, 0
    for series in obs_series:
        rv = process_observation_series(sesh, series)
        successes += rv['successes']
        skips += rv['skips']
        failures += rv['failures']
    return {'successes': successes, 'skips': skips, 'failures': failures}


def process_observation_series(sesh, os):

    try:
        stn_id = os.xpath("./origin/id[@type='client']")[0].text.strip()
    except IndexError as e:
        raise Exception(
            "Could not detect the station id: xpath search "
            "'//observation-series/origin/id[@type='client']' return no "
            "results")

    hist = check_history(stn_id, sesh)
    log.debug('Got history_id {}'.format(hist.id))
    members = os.xpath('./observation', namespaces=ns)
    log.debug("Found {} members for station {}".format(len(members), stn_id))

    successes, failures, skips = 0, 0, 0
    for member in members:
        t = member.get('valid-time')
        if not t:
            log.warn(
                "Could not find a valid-time attribute for this observation")
            continue
        # strip the timezone
        # remove this until we have a timezone respecting database
        # tz = pytz.timezone('America/Vancouver')
        # t = datetime.strptime(t[:-6], '%Y-%m-%dT%H:%M:%S')
        # t = tz.localize(t).astimezone(pytz.utc)

        for obs in member.iterchildren():
            varname = obs.tag
            vartype = obs.get('type')
            try:
                value_element = obs.xpath('./value')[0]
            except IndexError as e:
                log.warn("Could not find the actual value for observation "
                         "{}/{}. xpath search './value' returned no results"
                         .format(varname, vartype))
                skips += 1
                continue

            units = value_element.get('units')
            try:
                value = float(value_element.text)
            except ValueError:
                log.warn("Could not convert value '{}' to a number. Skipping "
                         "this observation.".format(value))
                skips += 1
                continue

            var = find_var(sesh, varname, vartype, units)
            if not var:
                # Test for known unwanted vars, only warn when unknown
                if (varname, vartype, units) not in unwanted_vars:
                    log.warn(("Could not find variable {}, {}, {} in the "
                             "database. Skipping this observation.")
                             .format(varname,
                                     vartype,
                                     units))
                skips += 1
                continue
            log.debug('{} {} {} {}'.format(varname, vartype, units, value))

            o = Obs(time=t, datum=float(value), variable=var, history=hist)

            # Regarding the following non-canonical but working code, see
            # https://github.com/pacificclimate/crmprtd/issues/9#issuecomment-348042673
            try:
                with sesh.begin_nested():
                    sesh.add(o)
                successes += 1
                sesh.commit()
                log.debug("Inserted {}".format(o))
            except IntegrityError as e:
                log.debug("Skipped, already exists: {} {}".format(o, e))
                sesh.rollback()
                skips += 1
            except Exception:
                log.error("Failed to insert {}".format(o), exc_info=True)
                sesh.rollback()
                failures += 1

    return {'successes': successes, 'skips': skips, 'failures': failures}


def find_var(sesh, varname, vartype, units):
    '''Returns a single Variable instance or None if it's not found'''
    q = sesh.query(Variable).join(Network).filter(Network.name == 'MoTIe')\
        .filter(Variable.name == vartype).filter(Variable.unit == units)
    return q.first()


def check_history(stn_id, sesh):
    log.debug('Lookup up history_id')
    hist = sesh.query(History).join(Station).join(Network).filter(
        Station.native_id == stn_id).filter(Network.name == 'MoTIe').first()
    if hist:
        return hist

    # No history id, check if station_id exists
    log.debug("History_id not found")
    stn = sesh.query(Station).join(Network).filter(
        Station.native_id == stn_id).filter(Network.name == 'MoTIe').first()
    if not stn:
        log.debug("Station_id not found")
        try:
            with sesh.begin_nested():
                stn = Station(native_id=stn_id, network=sesh.query(
                    Network).filter(Network.name == 'MoTIe').first())
                sesh.add(stn)
        except Exception as e:
            log.error("Station '{}' does not exist in the database and could "
                      "not be added".format(stn_id), exc_info=True)
            raise e
        log.debug('Created station_id {}'.format(stn.id))

    # Station_id added or exists, create history_id
    try:
        with sesh.begin_nested():
            hist = History(station=stn)
            sesh.add(hist)
    except Exception as e:
        log.error(
            'History_id could not be found or created for native_id {}'.format(
                stn_id), exc_info=True)
        raise e
    log.debug('Created history_id {}'.format(hist.id))

    return hist


def url_generator(station, from_, to, report='7110', request='historic'):
    if not isinstance(from_, datetime):
        raise ValueError("from_ paramater is not a datetime, but must be")
    if not isinstance(to, datetime):
        raise ValueError("to_ paramater is not a datetime, but must be")

    tz = pytz.timezone('America/Vancouver')
    # The MoTI app seems to accept its parameters in localtime
    from_ = from_.astimezone(tz)
    to = to.astimezone(tz)

    # Truncate to nearest hour
    from_ = from_.replace(minute=0, second=0, microsecond=0)
    to = to.replace(minute=0, second=0, microsecond=0)

    max_span = timedelta(days=6)
    timestep = timedelta(hours=1)
    t = from_
    while t < to:
        start = t
        end = min(to, t + max_span)
        yield makeurl(report, request, station, start, end)
        t = end + timestep


def slice_timesteps(start_date, end_date):
    if not isinstance(start_date, datetime):
        raise ValueError("start_date paramater is not a datetime, but must be")
    if not isinstance(end_date, datetime):
        raise ValueError("to_ paramater is not a datetime, but must be")
    assert start_date.tzinfo and end_date.tzinfo, ("Dates must be localized "
                                                   "and have tzinfo")

    tz = pytz.timezone('America/Vancouver')
    # The MoTI app seems to accept its parameters in localtime
    start_date = start_date.astimezone(tz)
    end_date = end_date.astimezone(tz)

    # Truncate to nearest hour
    start_date = start_date.replace(minute=0, second=0, microsecond=0)
    end_date = end_date.replace(minute=0, second=0, microsecond=0)

    max_span = timedelta(days=7)
    timestep = timedelta(hours=1)
    t = start_date
    while t < end_date:
        start = t
        end = min(end_date, t + max_span)
        yield (start, end)
        t = end + timestep
