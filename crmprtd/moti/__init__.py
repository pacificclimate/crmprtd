from pkg_resources import resource_filename
from datetime import datetime, timedelta
import logging

import pytz
from lxml.etree import parse, XSLT


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
