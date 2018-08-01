from pkg_resources import resource_filename
from datetime import datetime, timedelta
import logging

import pytz
from lxml.etree import parse, XSLT
from sqlalchemy.exc import IntegrityError

from pycds import History, Network, Station, Variable, Obs
from crmprtd import Timer

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
