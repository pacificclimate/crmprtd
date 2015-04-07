from pkg_resources import resource_filename
from datetime import datetime

import pytz
from lxml.etree import fromstring, parse, XSLT
import pytest

from pycds import Obs
from crmprtd.moti import process, url_generator, slice_timesteps

bctz = pytz.timezone('America/Vancouver')

def test_insert(session, moti_sawr7110_xml):
    tz = pytz.timezone('America/Vancouver')

    process(session, moti_sawr7110_xml)
    q = session.query(Obs)
    obs = q.all()
    assert len(obs) == 2
    actual = [pytz.utc.localize(o.time) for o in obs]
    expected = [ datetime(2012, 1, 1, tzinfo=tz), datetime(2012, 1, 1, 1, tzinfo=tz) ]
    assert actual == expected

def test_catch_duplicates(session, moti_sawr7110_xml):
    print 'test_catch_duplicates'
    rv = process(session, moti_sawr7110_xml)
    print '############## {}'.format(rv)
    assert rv == {'failures': 0, 'successes': 2, 'skips': 2}
    rv = process(session, moti_sawr7110_xml)
    print '################ {}'.format(rv)
    assert rv == {'failures': 0, 'successes': 0, 'skips': 6}
    
@pytest.mark.parametrize(('label','xml'),
                         [('no_obs', fromstring('''<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <data>
    <observation-series>
      <origin type="station">
        <id type="client">11091</id>
      </origin>
    </observation-series>
  </data>
</cmml>''')),
                         ('no_valid_time', fromstring('''<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <data>
    <observation-series>
      <origin type="station">
	<id type="client">11091</id>
      </origin>
      <observation>
	<pressure index="1" type="atmospheric">
	  <value units="mb">964
	  </value>
	</pressure>
      </observation>
    </observation-series>
  </data>
</cmml>''')),
                         ('bad_value', fromstring('''<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <data>
    <observation-series>
      <origin type="station">
	    <id type="client">11091</id>
      </origin>
      <observation>
        <pressure index="1" type="atmospheric">
	      <value units="mb">Not Convertible to a number</value>
        </pressure>
      </observation>
    </observation-series>
  </data>
</cmml>''')),
                         ('no_value', fromstring('''<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <data>
    <observation-series>
      <origin type="station">
	    <id type="client">11091</id>
      </origin>
      <observation>
        <pressure index="1" type="atmospheric">
        </pressure>
      </observation>
    </observation-series>
  </data>
</cmml>''')),
                         ('no_units', fromstring('''<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <data>
    <observation-series>
      <origin type="station">
	    <id type="client">11091</id>
      </origin>
      <observation>
        <pressure index="1" type="atmospheric">
	      <value>2.0</value>
        </pressure>
      </observation>
    </observation-series>
  </data>
</cmml>'''))])
def test_broken_obs(session, label, xml):
    n_obs_before = session.query(Obs).count()
    process(session, xml)
    n_obs_after = session.query(Obs).count()
    assert n_obs_before == n_obs_after
    
def test_missing_client_id(session):
    et = fromstring('''<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\Schema\CMML.xsd" version="2.01">
  <head>
  </head>
  <data>
    <observation-series>
      <origin type="station" />
    </observation-series>
  </data>
</cmml>''')
    e = pytest.raises(Exception, process, session, et)
    assert e.value.message == "Could not detect the station id: xpath search '//observation-series/origin/id[@type='client']' return no results"

def test_url_generator():
    urls = url_generator('1', bctz.localize(datetime(2010, 1, 1)), bctz.localize(datetime(2010, 3, 1)))
    actual = [url for url in urls]
    expected = ['https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-01-01/00&to=2010-01-08/00',
                'https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-01-08/01&to=2010-01-15/01',
                'https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-01-15/02&to=2010-01-22/02',
                'https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-01-22/03&to=2010-01-29/03',
                'https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-01-29/04&to=2010-02-05/04',
                'https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-02-05/05&to=2010-02-12/05',
                'https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-02-12/06&to=2010-02-19/06',
                'https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-02-19/07&to=2010-02-26/07',
                'https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-02-26/08&to=2010-03-01/00']
    assert  actual == expected

def test_url_generator_truncates():
    urls = url_generator('1', bctz.localize(datetime(2010, 1, 1, 1, 1)), bctz.localize(datetime(2010, 1, 1, 23, 55)))
    actual = [ url for url in urls ]
    expected = ['https://apps.th.gov.bc.ca/saw-data/sawr7110?request=historic&station=1&from=2010-01-01/01&to=2010-01-01/23']
    assert actual == expected

def test_url_generator_backwards_dates():
    urls = url_generator('1', bctz.localize(datetime(2012, 1, 1)), bctz.localize(datetime(2010, 1, 1)))
    actual = [ url for url in urls ]
    expected = []
    assert actual == expected

def test_var_transforms(moti_sawr7110_xml):
    xsl = resource_filename('crmprtd', 'data/moti.xsl')
    transform = XSLT(parse(xsl))
    et = transform(moti_sawr7110_xml)
    # Make sure that we can find some of the things to which we transformed
    assert et.xpath("/cmml/data/observation-series/observation/temperature[@type='CURRENT_AIR_TEMPERATURE1']")
    assert et.xpath("/cmml/data/observation-series/observation/temperature/value[@units='celsius']")
    assert et.xpath("/cmml/data/observation-series/observation/pressure[@type='ATMOSPHERIC_PRESSURE']")

def test_timestep_slices():
    d1 = bctz.localize(datetime(2010, 1, 1))
    d2 = bctz.localize(datetime(2010, 1, 15))
    results = [x for x in slice_timesteps(d1, d2)]
    expected = [(bctz.localize(datetime(2010, 1, 1)), bctz.localize(datetime(2010, 1, 8))),
                (bctz.localize(datetime(2010, 1, 8, 1)), bctz.localize(datetime(2010, 1, 15)))]
    assert results == expected
