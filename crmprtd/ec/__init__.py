from lxml.etree import LxmlError
from datetime import datetime
import logging
from urllib.parse import urlparse

from pycds import Network, Obs, Variable
from sqlalchemy.exc import IntegrityError


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
    fname = '{}_{}_{}_{}.xml'.format(
        freq, province.lower(), time.strftime(fmt), language)
    str = 'http://dd.weatheroffice.ec.gc.ca/observations/xml/'
    return str + '{}/{}/{}'.format(province.upper(), freq, fname)


def extract_fname_from_url(url):
    p = urlparse(url).path
    return p.split('/')[-1]


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
