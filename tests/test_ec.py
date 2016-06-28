from pkg_resources import resource_filename
from datetime import datetime

import pytz
from lxml.etree import fromstring, parse, XSLT
import pytest

from crmprtd.ec import makeurl, parse_xml, ObsProcessor, check_history, insert_obs

@pytest.mark.parametrize(('label', 'args','expected'), [
    ('daily-BC-EN',
     {'freq':'daily',
      'province': 'BC',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/yesterday/yesterday_bc_20160115_e.xml'
    ), ('hourly-BC-EN',
     {'freq':'hourly',
      'province': 'BC',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_2016011521_e.xml'
    ), ('nofreq-BC-EN',
     {'province': 'BC',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/yesterday/yesterday_bc_20160115_e.xml'
    ), ('hourly-noprov-EN',
     {'freq':'hourly',
      'language': 'e',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_2016011521_e.xml'
    ), ('hourly-BC-nolang',
     {'freq':'hourly',
      'province': 'BC',
      'time': datetime(2016, 1, 15, 21)},
     'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_2016011521_e.xml'
    )
])
def test_makeurl(label, args, expected):
    assert makeurl(**args) == expected

def test_makeurl_no_time_hourly():
    url = makeurl(freq='hourly')
    fmt = '%Y%m%d%H'
    t = datetime.utcnow()

    assert url == 'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/hourly/hourly_bc_{}_e.xml'.format(t.strftime(fmt))

def test_makeurl_no_time_daily():
    url = makeurl()
    fmt = '%Y%m%d'
    t = datetime.utcnow()

    assert url == 'http://dd.weatheroffice.ec.gc.ca/observations/xml/BC/yesterday/yesterday_bc_{}_e.xml'.format(t.strftime(fmt))
