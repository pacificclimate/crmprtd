from lxml.etree import parse, tostring, XSLT
from lxml.etree import LxmlError, XSLTError
from datetime import datetime
import psycopg2
import re
import logging
from traceback import format_exc
from pkg_resources import resource_stream

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
    return {'url': 'http://dd.weatheroffice.ec.gc.ca/observations/xml/%s/%s/%s' % (province.upper(), freq, fname),
            'filename': fname}

class ObsProcessor:
    def __init__(self, xml_filename, prefs):
        """Take one file(-like object) of Meteorological Point Observation XML (mpo-xml)
        and do everything required to get it into the CRMP database
        prefs should be an object of type optparse.Values with attributes: connection_string, log, cache_dir, error_email
        raises: lxml.etree.LxmlSyntaxError, IOError, psycopg2.OperationalError
        """

        # set variables for summary information
        self._members = 0
        self._members_processed = 0
        self._member_errors = 0
        self._obs = 0
        self._obs_errors = 0
        self._obs_insertions = 0
        
        self.prefs = prefs
        log.debug("Parsing xml")
        self.et = parse(xml_filename)
        log.debug("Opening database connection")
        self.conn = psycopg2.connect(prefs.connection_string)
        self._diagnostic_mode = self.prefs.diag

    def process(self):
        if self._diagnostic_mode: log.info("DIAGNOSTIC MODE, NO RECORDS WILL BE COMMITTED")
        # Apply a transformation to customize the EC records to our needs
        try:
            log.debug("Applying transformation")
            xsl = resource_stream(__name__, 'data/ec_xform.xsl')
            transform = XSLT(parse(xsl))
            self.et = transform(self.et)
            log.debug("Transformation applied")
        # Non-fatal; there still lots of raw observations that we can record and pick up the rest later after the XSL is fixed
        except XSLTError as e:
            log.exception("Failed to apply XLST ec_xform.xsl")
        
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
        log.debug("Opening cursor")
        cur = self.conn.cursor()
        try:
            cur.execute("SAVEPOINT obs_save") # Set a savepoint to rollback to for minor errors
            hid = check_history(member, cur, self.prefs.thresh)
            log.debug("Found history id: {0}".format(hid))
            if hid == None:
                log.debug("Unable to find or create history id for member below\n{0}\n\n".format(tostring(member, pretty_print=True)))
                return

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

        except psycopg2.InternalError, e:
            log.exception("Error processing member. Member has been saved in logs.")
            log.debug("Error processing member:\n{0}".format(tostring(member,pretty_print=True)))
            self.conn.rollback()
        finally:
            cur.close()

    def save(self, filename, mode='w'):
        f = open(filename, mode)
        print >>f, tostring(self.et, pretty_print=True)

def check_history(member, cur, threshold):

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
        log.debug("Could not find station attributes, likely not a station")
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
    q = cur.mogrify("""
    SELECT history_id, freq
    FROM meta_history NATURAL JOIN meta_station NATURAL JOIN meta_network
    WHERE network_name = 'EC_raw' AND native_id = %s AND station_name = %s
    AND sdate <= %s AND (edate >= %s OR edate IS NULL)
    AND history_id IN (SELECT history_id FROM closest_stns_within_threshold(%s, %s, %s))
    """, (native_id, stn_name, obs_time, obs_time, lon, lat, threshold))
    log.debug("Query text:\n{0}".format(q))
    cur.execute(q)

    # Could return 0-1 results  ## FIXME - should process in order of (ideal) likelihood: 1 record (always), no record (perhaps), multiple records (ideally never) 

    if cur.rowcount > 1:
        ## FIXME - handle multiple results appropriately
        raise Exception("Found {rc} relevant history_id entries for station name {sn} native id {nid}, unable to process".format(rc=cur.rowcount,sn=stn_name,nid=native_id))
    record = cur.fetchone()
    if record:
        hid, db_freq = record
        log.debug("Found history id {0}".format(hid))
        # 'Upgrade' the frequency if we're receiving hourly results for a station marked as daily
        if db_freq == 'daily' and freq == '1-hourly':
            log.debug("Upgrading frequency to hourly")
            q = cur.mogrify("UPDATE meta_history SET freq = %s WHERE history_id = %s", (freq, hid))
            cur.execute(q)
        return hid

    log.debug("No matching open history_id found")
    # Stuff may not match because:
    #   -This a new station/native_id
    #   -A station as moved but kept old identifying information
    #   -A station has a new name
    #   -A station that was previously 'closed' has started reporting again
    # First close out the old history_id if it exists
    q = cur.mogrify("""
    SELECT station_id, history_id, max(obs_time)
    FROM obs_raw NATURAL JOIN meta_history NATURAL JOIN meta_station NATURAL JOIN meta_network
    WHERE network_name = 'EC_raw' AND native_id = %s AND edate IS NULL
    GROUP BY station_id, history_id
    """, (native_id,))
    cur.execute(q)

    ## TODO: handle possible case of multple records
    if cur.rowcount > 1:
        log.debug("Multiple open but not entirely matching records found for this member")
        raise Exception("Multiple open records with same native_id {0} found in member".format(native_id))

    record = cur.fetchone()
    if record:
        stn_id, hid, tn = record
        log.debug("Closing history_id {0}".format(hid))
        q = cur.mogrify("UPDATE meta_history SET edate = %s WHERE history_id = %s AND edate IS NULL", (tn, hid))
        cur.execute(q)
    # If it doesn't exist, this is a new station so create a new station_id
    else:
        q = cur.mogrify("INSERT INTO meta_station (native_id, network_id) VALUES (%s, (SELECT network_id FROM meta_network WHERE network_name = 'EC_raw')) RETURNING station_id", (native_id,))
        cur.execute(q)
        stn_id = cur.fetchone()[0]
        log.debug("Created new station_id {0}".format(stn_id))

    # Insert the new meta_history entry
    q = cur.mogrify("INSERT INTO meta_history (station_name, station_id, lat, lon, sdate, freq) VALUES (%s, %s, %s, %s, %s, %s) RETURNING history_id", (stn_name, stn_id, lat, lon, obs_time, freq))
    cur.execute(q)
    hid = cur.fetchone()[0]
    log.debug("Created new meta_history entry with id {0}".format(hid))
    update_geom(cur)
    cur.execute("SAVEPOINT obs_save") 

    return hid

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
