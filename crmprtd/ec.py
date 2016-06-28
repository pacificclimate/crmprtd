from lxml.etree import LxmlError, parse, tostring, XSLT
from datetime import datetime
import re
import logging
from pkg_resources import resource_stream
from urlparse import urlparse

from pycds import *
from sqlalchemy import and_, or_
from sqlalchemy.sql import func

log = logging.getLogger(__name__)

ns = {
    'om': 'http://www.opengis.net/om/1.0',
    'mpo': "http://dms.ec.gc.ca/schema/point-observation/2.1",
    'gml': "http://www.opengis.net/gml",
    'xlink': "http://www.w3.org/1999/xlink",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
    }

def makeurl(freq='daily', province='BC', language='e', time=datetime.utcnow()):
    """Construct a URL for fetching the data file
    freq: daily|hourly
    province: 2 letter province code
    language: 'e' (english) | 'f' (french)
    time: datetime object of the time for which you want to fetch obs
    """
    fmt = '%Y%m%d%H' if freq == 'hourly' else '%Y%m%d'
    freq = 'yesterday' if freq == 'daily' else freq
    fname = '%s_%s_%s_%s.xml' % (freq, province.lower(), time.strftime(fmt), language)
    return 'http://dd.weatheroffice.ec.gc.ca/observations/xml/%s/%s/%s' % (province.upper(), freq, fname)

def extract_fname_from_url(url):
    path = urlparse(url)['path']
    return path.split('/')[-1]

def parse_xml(fname):
    # Parse and transform the xml
    et = parse(fname)
    xsl = resource_stream('crmprtd', 'data/ec_xform.xsl')
    transform = XSLT(parse(xsl))
    return transform(et)

class ObsProcessor:
    def __init__(self, et, sesh, threshold, diag):
        # set variables for summary information
        self._members = 0
        self._members_processed = 0
        self._member_errors = 0
        self._obs = 0
        self._obs_errors = 0
        self._obs_insertions = 0

        self.et = et
        self.sesh = sesh
        self.threshold = threshold
        self._diagnostic_mode = diag

    def process(self):
        if self._diagnostic_mode: log.info("DIAGNOSTIC MODE, NO RECORDS WILL BE COMMITTED")
        
        members = self.et.xpath('//om:member', namespaces=ns)
        self._members = len(members)
        log.info("Found {} members in the xml".format(self._members))

        for member in members:
            try:
                log.debug("Processing next member")
                self.process_member(member)
                self._members_processed += 1
            except Exception as e: # FIXME: More specific exception handling
                self._member_errors += 1
                log.exception("Error processing member.  Member has been saved in logs")
                log.debug("Error processing member:\n{0}".format(tostring(member, pretty_print=True)))

        log.info("Finished processing {mp}/{mt} members and inserted {oi}/{ot} insertable observations".format(mp=self._members_processed, mt=self._members, oi=self._obs_insertions, ot=self._obs))
        if self._member_errors or self._obs_errors:
            raise Exception('''Unable to parse {me} members,
            Unable to insert {oe} insertable obs'''.format(me=self._member_errors, oe=self._obs_errors))


    def process_member(self, member):
        hid = check_history(member, self.sesh, self.threshold)
        log.debug("Found history id: {0}".format(hid))
        if hid == None:
            # This is not a station
            return

        return # Debug to here

        om = OmMember(member)
        log.debug("Member unit initialized")

        rec_vars = recordable_vars(self.conn)
        insert_vars = set(om.observed_vars()).intersection(rec_vars.keys())
        log.debug("Insertable variables: {0}".format(insert_vars))

        for vname in insert_vars:
            vid = rec_vars[vname]
            try:
                self._obs += 1
                insert_obs(cur, om, hid, vname, vid) # FIMXE: handle units errors (assertionError)
                self._obs_insertions += 1
            except Exception, e:
                log.exception("Unable to insert this observation")
                self._obs_errors += 1

        # Remove member from XML "processing queue"
        if len(om.member.xpath("./om:Observation/om:result//mpo:element", namespaces=ns)) == 0:
            member.getparent().remove(member)

        if not self._diagnostic_mode:
            self.conn.commit()

def check_history(member, sesh, threshold):
    '''
    Returns None if member does not have station attributes
    '''

    attrs = ['station_name', 'climate_station_number']
    # Select critical information from XML
    try:
        log.debug("Finding Station attributes")
        stn_name, native_id = map(lambda x: member.xpath(".//mpo:identification-elements/mpo:element[@name='%s']" % x, namespaces=ns)[0].get('value'), attrs)
        lat, lon = map(float, member.xpath('.//gml:pos', namespaces=ns)[0].text.split())
        obs_time = member.xpath('./om:Observation/om:samplingTime//gml:timePosition', namespaces=ns)[0].text
        log.debug("Found station name {name}, id {id}, at {lon}, {lat}, with obs at {t}".format(name=stn_name, id=native_id, lon=lon, lat=lat, t=obs_time))
    # An IndexError here means that the member has no station_name or climate_station_number (or identification-elements),
    # lat/lon, or obs_time in which case we don't need to process this item
    except IndexError:
        log.debug("This member does not appear to be a station")
        return None

    # Determine the frequency for this station
    log.debug("Finding station frequency")
    dataset = member.xpath('.//mpo:dataset', namespaces=ns)[0].get('name')
    if re.search('product-hourly', dataset) or re.search('hour_summary', dataset):
        freq = '1-hourly'
    elif re.search('product-today', dataset) or re.search('product-yesterday', dataset) or re.search('yesterday_summary', dataset):
        freq = 'daily'
    else:
        raise Exception("Could not determine frequency for a meta_history insertion.  Unexpected product: %s", dataset)
    log.debug("Found frequency {0}".format(freq))

    # Select all history entries that match this station
    log.debug("Searching for matching meta_history entries")

    q = sesh.execute('SELECT history_id from closest_stns_within_threshold(:lon, :lat, :threshold)', 
        {'lon': lon, 'lat': lat, 'threshold': threshold})
    valid_hid = set([x[0] for x in q.fetchall()])

    q = sesh.query(History.id, History.freq).join(Station).join(Network)\
        .filter(Station.native_id == native_id).filter(Network.name == 'EC_raw')\
        .filter(and_(
            or_(History.sdate <= obs_time, History.sdate.is_(None)), 
            or_(History.edate >= obs_time, History.edate.is_(None))
        ))\
        .filter(History.station_name == stn_name)
    r = q.all()

    # log.info(histories)

    possible_hist = [hist for hist in r if hist.id in valid_hid]

    if len(possible_hist) == 1:
        # We've got a hit
        hist = possible_hist[0]
        hid, db_freq = hist.id, hist.freq
        log.debug('Found hid: {}'.format(hid))

        # 'Upgrade' the frequency if we're receiving hourly results for a station marked as daily
        if db_freq == 'daily' and freq == '1-hourly':
            log.debug("Upgrading frequency to hourly")
            hist.freq = freq

        return hid

    if len(possible_hid) < 1:
        log.debug("No matching open history_id found")
        # Stuff may not match because:
        #   -This a new station/native_id
        #   -A station as moved but kept old identifying information
        #   -A station has a new name
        #   -A station that was previously 'closed' has started reporting again

        # First close out the old history_id if it exists

# -    SELECT station_id, history_id, max(obs_time)
# -    FROM obs_raw NATURAL JOIN meta_history NATURAL JOIN meta_station NATURAL JOIN meta_network
# -    WHERE network_name = 'EC_raw' AND native_id = %s AND edate IS NULL
# -    GROUP BY station_id, history_id
# -    """, (native_id,))
# -    cur.execute(q)


        q = sesh.query(History, func.max(Obs.time).label('max_time')).join(Obs).join(Station).join(Network)\
            .filter(Station.native_id == native_id).filter(Network.name == 'EC_raw')\
            .fitler(History.edate.is_(None))
        r = q.all()

        if len(r) > 1:
            ## TODO: handle possible case of multple records
            log.debug("Multiple open records found for this member")
            raise Exception("Multiple open records with same native_id {0} found in member".format(native_id))

        if len(r) == 1:
            pass
        # stn_id, hid, tn = record
        # log.debug("Closing history_id {0}".format(hid))
        # q = cur.mogrify("UPDATE meta_history SET edate = %s WHERE history_id = %s AND edate IS NULL", (tn, hid))
        # cur.execute(q)

        else:
            pass
            # # If it doesn't exist, this is a new station so create a new station_id
            # else:
            #     q = cur.mogrify("INSERT INTO meta_station (native_id, network_id) VALUES (%s, (SELECT network_id FROM meta_network WHERE network_name = 'EC_raw')) RETURNING station_id", (native_id,))
            #     cur.execute(q)
            #     stn_id = cur.fetchone()[0]
            #     log.debug("Created new station_id {0}".format(stn_id))

            # # Insert the new meta_history entry
            # q = cur.mogrify("INSERT INTO meta_history (station_name, station_id, lat, lon, sdate, freq) VALUES (%s, %s, %s, %s, %s, %s) RETURNING history_id", (stn_name, stn_id, lat, lon, obs_time, freq))
            # cur.execute(q)
            # hid = cur.fetchone()[0]
            # log.debug("Created new meta_history entry with id {0}".format(hid))
            # update_geom(cur)
            # cur.execute("SAVEPOINT obs_save") 

            # return hid


    # Must be multiple potentially valid history_id's.
    # FIXME: handle this more appropriately than screaming
    raise Exception("Found {rc} relevant history_id entries for station name {sn} native id {nid}, unable to process".format(rc=len(possible_hid),sn=stn_name,nid=native_id))


def insert_obs(cur, om, hid, vname, vid):

    try:
        assert db_unit(cur, vname) == om.member_unit(vname)
    except:
        # UnitsError
        raise Exception("reported units '%s' does not match the database units '%s' for variable %s" % (om.member_unit(vname), db_unit(cur, vname), vname))

    t = om.member.xpath('./om:Observation/om:samplingTime//gml:timePosition', namespaces=ns)[0].text

    try:
        ele = om.member.xpath("./om:Observation/om:result//mpo:element[@name='%s']" % vname, namespaces=ns)[0]
        val = float(ele.get('value'))
    # This shouldn't every be empty based on our xpath for selecting elements... however I think that it _could_ be non-numeric and still be valid XML
    except ValueError, e:
        raise e

    q = cur.mogrify("INSERT INTO obs_raw (obs_time, datum, vars_id, history_id) VALUES (%s, %s, %s, %s)", (t, val, vid, hid))
    try:
        cur.execute(q)
        cur.execute('SAVEPOINT obs_save')
        log.debug("Inserted obs using query: {0}".format(q))
    # On the event of a unique constraint error or aborted transaction respectively
    except (psycopg2.IntegrityError, psycopg2.InternalError), e:
        cur.execute('ROLLBACK TO obs_save')
        log.exception("Problem inserting observation with query {0}".format(q))
        raise e
    # DataError (invalid input sytax), ProgrammingError (column does not exist)
    except (psycopg2.DataError, psycopg2.ProgrammingError), e:
        # FIXME
        raise e
    else:
        ele.getparent().remove(ele) # Remove element from XML "processing queue"
        log.debug("Element removed from processing queue")

def recordable_vars(conn):
    q = "SELECT net_var_name, vars_id FROM meta_vars NATURAL JOIN meta_network WHERE network_name = 'EC_raw'"
    cur = conn.cursor()
    cur.execute(q)
    return dict(cur.fetchall())

def update_geom(cur):
    '''Update the geometry column based on the lat/lon fields
       FIXME: There is some question that this may not be updating; check for sure'''
    cur.execute('UPDATE meta_history SET the_geom = ST_SetSRID(ST_Point(lon,lat),4326)')

def db_unit(cur, var_name):
    q = cur.mogrify("SELECT unit FROM meta_vars NATURAL JOIN meta_network WHERE network_name = 'EC_raw' AND net_var_name = %s", (var_name,))
    cur.execute(q)
    try:
        return cur.fetchone()[0]
    except IndexError: # zero rows
        return None

class OmMember:
    def __init__(self, member):
        self.member = member

    def member_unit(self, v):
        '''Returns the unit of the element measuring the quantity v
           If v is not one of the elements, raises LxmlError
        '''
        try:
            return self.member.xpath("./om:Observation/om:result/mpo:elements/mpo:element[@name='%s']" % v, namespaces=ns)[0].get('uom')
        except IndexError:
            raise LxmlError("%s is not one of the mpo:elements in this om:member" % v)

    def observed_vars(self):
        '''Returns the names of all quantities specified by this member
        '''
        return [e.get('name') for e in self.member.xpath(".//om:result/mpo:elements/mpo:element[@name!=''][@value!='']", namespaces=ns)]
