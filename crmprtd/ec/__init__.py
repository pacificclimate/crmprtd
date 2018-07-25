from lxml.etree import tostring, LxmlError
from datetime import datetime
import re
import yaml
import logging
from urllib.parse import urlparse

from pycds import History, Station, Network, Obs, Variable
from sqlalchemy import and_, or_
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from crmprtd import Timer


log = logging.getLogger(__name__)
ns = {
    'om': 'http://www.opengis.net/om/1.0',
    'mpo': "http://dms.ec.gc.ca/schema/point-observation/2.1",
    'gml': "http://www.opengis.net/gml",
    'xlink': "http://www.w3.org/1999/xlink",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}


def logging_setup(log_conf, log, error_email, log_level):
    with open(log_conf, 'rb') as f:
        log_conf = yaml.load(f)
    if log:
        log_conf['handlers']['file']['filename'] = log
    else:
        log = log_conf['handlers']['file']['filename']
    if error_email:
        log_conf['handlers']['mail']['toaddrs'] = error_email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger('crmprtd.ec')
    if log_level:
        log.setLevel(log_level)

    return log


def makeurl(freq='daily', province='BC', language='e', time=datetime.utcnow()):
    """Construct a URL for fetching the data file
    freq: daily|hourly
    province: 2 letter province code
    language: 'e' (english) | 'f' (french)
    time: datetime object of the time for which you want to fetch obs
    """
    fmt = '%Y%m%d%H' if freq == 'hourly' else '%Y%m%d'
    freq = 'yesterday' if freq == 'daily' else freq
    fname = '{}_{}_{}_{}.xml'.format(
        freq, province.lower(), time.strftime(fmt), language)
    str = 'http://dd.weatheroffice.ec.gc.ca/observations/xml/'
    return str + '{}/{}/{}'.format(province.upper(), freq, fname)


def extract_fname_from_url(url):
    p = urlparse(url).path
    return p.split('/')[-1]


class ObsProcessor:
    def __init__(self, et, sesh, threshold):
        # set variables for summary information
        self._members = 0
        self._members_processed = 0
        self._member_errors = 0
        self._obs = 0
        self._obs_errors = 0
        self._obs_insertions = 0
        self._obs_existing = 0

        self.et = et
        self.sesh = sesh
        self.threshold = threshold

    def process(self):
        log.info('Processing data')
        members = self.et.xpath('//om:member', namespaces=ns)
        self._members = len(members)
        log.debug("Found members in the xml",
                  extra={'num_members': self._members})

        with Timer() as tmr:
            for member in members:
                try:
                    log.debug("Processing next member")
                    self.process_member(member)
                    self._members_processed += 1
                # FIXME: More specific exception handling
                except Exception as e:
                    self._member_errors += 1
                    log.exception("Error processing member, saved in logs")
                    log.error('Error processing member',
                              extra={'member': tostring(member,
                                                        pretty_print=True)})

        log.info("Finished processing",
                 extra={'num_members': self._members,
                        'num_members_processed': self._members_processed,
                        'inserted': self._obs_insertions,
                        'obs': self._obs,
                        'skipped': self._obs_existing,
                        'insertions_per_sec': (self._obs_insertions /
                                               tmr.run_time)})

        if self._member_errors or self._obs_errors:
            raise Exception('''Unable to parse {me} members,
            Unable to insert {oe} insertable obs'''.format(
                me=self._member_errors, oe=self._obs_errors))

    def process_member(self, member):
        hid = check_history(member, self.sesh, self.threshold)
        log.debug("Found history id", extra={'hid': hid})
        if hid is None:
            # This is not a station
            return

        om = OmMember(member)
        log.debug("Member unit initialized")

        rec_vars = recordable_vars(self.sesh)
        insert_vars = set(om.observed_vars()).intersection(rec_vars.keys())
        log.debug("Insertable variables", extra={'variables': insert_vars})

        for vname in insert_vars:
            vid = rec_vars[vname]
            try:
                self._obs += 1
                # FIMXE: handle units errors (assertionError)
                inserted = insert_obs(self.sesh, om, hid, vname, vid)
                if inserted:
                    self._obs_insertions += 1
                else:
                    self._obs_existing += 1
            except Exception as e:
                log.exception("Unable to insert this observation")
                self._obs_errors += 1

        # Remove member from XML "processing queue"
        if len(om.member.xpath("./om:Observation/om:result//mpo:element",
           namespaces=ns)) == 0:
            member.getparent().remove(member)


def closest_stns_within_threshold(sesh, lon, lat, threshold):
    # Select all history entries that match this station
    log.debug("Searching for matching meta_history entries")

    query_txt = """
        WITH stns_in_thresh AS (
            SELECT history_id, lat, lon, Geography(ST_Transform(the_geom,4326)) as p_existing,
                Geography(ST_SetSRID(ST_MakePoint(:x, :y),4326)) as p_new
            FROM crmp.meta_history
            WHERE the_geom && ST_Buffer(Geography(ST_SetSRID(ST_MakePoint(:x, :y), 4326)),:thresh)
        )
        SELECT history_id, ST_Distance(p_existing,p_new) as dist
        FROM stns_in_thresh
        ORDER BY dist
""" # noqa
    q = sesh.execute(query_txt, {
        'x': lon,
        'y': lat,
        'thresh': threshold}
    )
    valid_hid = set([x[0] for x in q.fetchall()])
    log.debug("history_ids in threshold", extra={'hid': valid_hid})
    return valid_hid


def check_history(member, sesh, threshold):
    '''
    Returns None if member does not have station attributes
    '''

    attrs = ['station_name', 'climate_station_number']
    # Select critical information from XML
    stn_name = None
    native_id = None
    lat = None
    lon = None
    obs_time = None
    try:
        log.debug("Finding Station attributes")
        stn_name, native_id = map(lambda x: member.xpath(
            ".//mpo:identification-elements/mpo:element[@name='%s']" %
            x, namespaces=ns)[0].get('value'), attrs)
        lat, lon = map(float, member.xpath(
            './/gml:pos', namespaces=ns)[0].text.split())
        obs_time = member.xpath(
            './om:Observation/om:samplingTime//gml:timePosition',
            namespaces=ns)[0].text
        log.debug('Found station info', extra={'station_name': stn_name,
                                               'station_id': native_id,
                                               'lon': lon,
                                               'lat': lat,
                                               'time': obs_time})
    # An IndexError here means that the member has no station_name or
    # climate_station_number (or identification-elements), lat/lon, or obs_time
    # in which case we don't need to process this item
    except IndexError:
        log.warning("This member does not appear to be a station",
                    extra={'station_name': stn_name,
                           'station_id': native_id,
                           'lon': lon,
                           'lat': lat})
        return None

    # Determine the frequency for this station
    log.debug("Finding station frequency")
    dataset = member.xpath('.//mpo:dataset', namespaces=ns)[0].get('name')
    if(re.search('product-hourly', dataset) or
       re.search('hour_summary', dataset)):
        freq = '1-hourly'
    elif(re.search('product-today', dataset) or
         re.search('product-yesterday', dataset) or
         re.search('yesterday_summary', dataset)):
        freq = 'daily'
    else:
        raise Exception(
            "Could not determine frequency for a meta_history insertion. "
            "Unexpected product: %s", dataset)
    log.debug("Found frequency", extra={'frequency': freq})

    valid_hid = closest_stns_within_threshold(sesh, lon, lat, threshold)

    q = sesh.query(History.id, History.freq).join(Station).join(Network)\
        .filter(Station.native_id == native_id)\
        .filter(Network.name == 'EC_raw')\
        .filter(and_(
            or_(History.sdate <= obs_time, History.sdate.is_(None)),
            or_(History.edate >= obs_time, History.edate.is_(None))
        ))\
        .filter(History.station_name == stn_name)
    r = q.all()
    log.debug("history_ids based on native_id, station_name, and data "
              "sdate/edate", extra={'query': r})

    possible_hist = [hist for hist in r if hist.id in valid_hid]

    if len(possible_hist) == 1:
        # We've got a hit
        hist = possible_hist[0]
        # db_freq = hist.freq
        hid = hist.id
        log.debug('Found hid', extra={'hid': hid})

        # 'Upgrade' the frequency if we're receiving hourly results for a
        # station marked as daily

        # TODO: Fix this code, it doens't work
        # if db_freq == 'daily' and freq == '1-hourly':
        #     log.debug("Upgrading frequency to hourly")
        #     hist.freq = freq

        return hid

    if len(possible_hist) < 1:
        log.debug("No matching open history_id found")
        # Stuff may not match because:
        #   -This a new station/native_id
        #   -A station as moved but kept old identifying information
        #   -A station has a new name
        #   -A station that was previously 'closed' has started reporting again

        # First close out the old history_id if it exists
        q = sesh.query(History, func.max(Obs.time).label('max_time'))\
            .join(Obs).join(Station).join(Network)\
            .filter(Station.native_id == native_id)\
            .filter(Network.name == 'EC_raw')\
            .filter(History.edate.is_(None))\
            .group_by(History.id, Station.id)
        r = q.all()

        if len(r) > 1:
            # TODO: handle possible case of multple records
            log.warning("Multiple open records found for this member")
            raise Exception("Multiple open records with same native_id {0} "
                            "found in member".format(native_id))

        # If we only have one record, close it out
        if len(r) == 1:
            hist, max_time = r[0]
            hist.edate = max_time

        q = sesh.query(Network).filter(Network.name == 'EC_raw')
        assert q.count() == 1
        ec = q.first()

        # If we have no record of that native_id, this is a new station and we
        # must insert it
        q = sesh.query(Station)\
                .filter(Station.native_id == native_id)\
                .filter(Station.network == ec)
        r = q.all()
        if len(r) < 1:
            stn = Station(native_id=native_id, network=ec)
            with sesh.begin_nested():
                sesh.add(stn)
            log.debug("Created new station_id", extra={'station_id': stn.id})

        elif len(r) > 1:
            raise Exception(
                "Multiple stations with native_id {0}. Panicing".format(
                    native_id))

        else:
            stn = r[0]

        # Insert the new meta_history entry
        hist = History(station_name=stn_name,
                       station=stn,
                       lon=lon,
                       lat=lat,
                       the_geom='SRID=4326;POINT({} {})'.format(lon, lat),
                       sdate=obs_time,
                       freq=freq)
        with sesh.begin_nested():
            sesh.add(hist)

        return hist.id

    # Must be multiple potentially valid history_id's.
    # FIXME: handle this more appropriately than screaming
    raise Exception("Found {rc} relevant history_id entries for station name "
                    "{sn} native id {nid}, unable to process".format(
                        rc=len(possible_hist), sn=stn_name, nid=native_id))


def insert_obs(sesh, om, hid, vname, vid):

    try:
        assert db_unit(sesh, vname) == om.member_unit(vname)
    except Exception:
        # UnitsError
        raise Exception("reported units '%s' does not match the database units"
                        " '%s' for variable %s" % (om.member_unit(vname),
                                                   db_unit(sesh, vname),
                                                   vname))

    t = om.member.xpath(
        './om:Observation/om:samplingTime//gml:timePosition',
        namespaces=ns)[0].text

    try:
        ele = om.member.xpath(
            "./om:Observation/om:result//mpo:element[@name='%s']" %
            vname, namespaces=ns)[0]
        val = float(ele.get('value'))
    # This shouldn't every be empty based on our xpath for selecting elements,
    # however I think that it _could_ be non-numeric and still be valid XML
    except ValueError as e:
        raise e

    o = Obs(time=t,
            datum=val,
            vars_id=vid,
            history_id=hid)
    try:
        with sesh.begin_nested():
            sesh.add(o)
    except IntegrityError as e:
        # Use psycopg2 wrapped 'orig' pgcode attribute
        if e.orig.pgcode == '23505':
            log.debug('Obs already exists')
            return False
        else:
            raise e
    else:
        log.debug("Added observation", extra={'value': o.datum,
                                              'variable': o.vars_id,
                                              'hid': o.history_id,
                                              'timestamp': o.time})
        # Remove element from XML "processing queue"
        ele.getparent().remove(ele)
        log.debug("Element removed from processing queue")

    return True


def recordable_vars(sesh):
    q = sesh.query(Variable.name, Variable.id).join(
        Network).filter(Network.name == 'EC_raw')
    return dict(q.all())


def db_unit(sesh, var_name):
    q = sesh.query(Variable.unit).join(Network)\
            .filter(Variable.name == var_name)\
            .filter(Network.name == 'EC_raw')
    r = q.all()
    try:
        return r[0][0]
    except IndexError:  # zero rows
        return None


class OmMember(object):
    def __init__(self, member):
        self.member = member

    def member_unit(self, v):
        '''Returns the unit of the element measuring the quantity v
           If v is not one of the elements, raises LxmlError
        '''
        try:
            return self.member.xpath("./om:Observation/om:result/mpo:elements"
                                     "/mpo:element[@name='%s']" %
                                     v, namespaces=ns)[0].get('uom')
        except IndexError:
            raise LxmlError(
                "%s is not one of the mpo:elements in this om:member" % v)

    def observed_vars(self):
        '''Returns the names of all quantities specified by this member
        '''
        return [e.get('name') for e in self.member.xpath(
                ".//om:result/mpo:elements/mpo:element[@name!=''][@value!='']",
                namespaces=ns)]
