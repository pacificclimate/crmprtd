from pkg_resources import resource_filename
from datetime import datetime

from lxml.etree import parse, XSLT
import pytz

from crmprtd.networks.moti import url_generator

bctz = pytz.timezone("America/Vancouver")


xml = {
    "no_obs": b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
  <data>
    <observation-series>
      <origin type="station">
        <id type="client">11091</id>
      </origin>
    </observation-series>
  </data>
</cmml>""",  # noqa
    "no_valid_time": b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
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
       </cmml>""",  # noqa
    "bad_value": b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
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
       </cmml>""",  # noqa
    "no_value": b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
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
       </cmml>""",  # noqa
    "no_units": b"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<cmml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="..\\Schema\\CMML.xsd" version="2.01">
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
 </cmml>""",
}  # noqa


def test_url_generator():
    urls = url_generator(
        "1", bctz.localize(datetime(2010, 1, 1)), bctz.localize(datetime(2010, 3, 1))
    )
    actual = [url for url in urls]
    expected = [
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-01-01/00&to=2010-01-07/00"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-01-07/01&to=2010-01-13/01"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-01-13/02&to=2010-01-19/02"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-01-19/03&to=2010-01-25/03"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-01-25/04&to=2010-01-31/04"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-01-31/05&to=2010-02-06/05"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-02-06/06&to=2010-02-12/06"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-02-12/07&to=2010-02-18/07"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-02-18/08&to=2010-02-24/08"
        ),
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-02-24/09&to=2010-03-01/00"
        ),
    ]
    assert actual == expected


def test_url_generator_truncates():
    urls = url_generator(
        "1",
        bctz.localize(datetime(2010, 1, 1, 1, 1)),
        bctz.localize(datetime(2010, 1, 1, 23, 55)),
    )
    actual = [url for url in urls]
    expected = [
        (
            "https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110?request="
            "historic&station=1&from=2010-01-01/01&to=2010-01-01/23"
        )
    ]
    assert actual == expected


def test_url_generator_backwards_dates():
    urls = url_generator(
        "1", bctz.localize(datetime(2012, 1, 1)), bctz.localize(datetime(2010, 1, 1))
    )
    actual = [url for url in urls]
    expected = []
    assert actual == expected


def test_var_transforms(moti_sawr7110_xml):
    xsl = resource_filename("crmprtd", "data/moti.xsl")
    transform = XSLT(parse(xsl))
    et = transform(moti_sawr7110_xml)
    # Make sure that we can find some of the things to which we transformed
    assert et.xpath(
        (
            "/cmml/data/observation-series/observation/"
            "temperature[@type='CURRENT_AIR_TEMPERATURE1']"
        )
    )
    assert et.xpath(
        "/cmml/data/observation-series/observation/"
        "temperature/value[@units='celsius']"
    )
    assert et.xpath(
        "/cmml/data/observation-series/observation/"
        "pressure[@type='ATMOSPHERIC_PRESSURE']"
    )


def test_var_transforms_all(moti_sawr7100_large):
    xsl = resource_filename("crmprtd", "data/moti.xsl")
    transform = XSLT(parse(xsl))
    et = transform(moti_sawr7100_large)
    assert et.xpath(
        (
            "/cmml/data/observation-series/observation/"
            "pressure[@type='ATMOSPHERIC_PRESSURE']"
        )
    )
    assert et.xpath(
        (
            "/cmml/data/observation-series/observation/"
            "wind[@type='MEASURED_WIND_SPEED1']"
        )
    )
    assert et.xpath(
        (
            "/cmml/data/observation-series/observation/"
            "wind[@type='MEASURED_WIND_DIRECTION1']"
        )
    )
    assert et.xpath(
        (
            "/cmml/data/observation-series/observation/"
            "wind[@type='WIND_DIRECTION_STD_DEVIATION1']"
        )
    )
    assert et.xpath(
        (
            "/cmml/data/observation-series/observation/"
            "temperature[@type='CURRENT_AIR_TEMPERATURE1']"
        )
    )
    assert et.xpath(
        ("/cmml/data/observation-series/observation/" "temperature[@type='DEW_POINT']")
    )
    assert et.xpath(
        (
            "/cmml/data/observation-series/observation/"
            "precipitation[@type='HOURLY_PRECIPITATION']"
        )
    )
    assert et.xpath(
        (
            "/cmml/data/observation-series/observation/"
            "humidity[@type='RELATIVE_HUMIDITY1']"
        )
    )
    assert et.xpath(
        ("/cmml/data/observation-series/observation/" "snow[@type='HEIGHT_OF_SNOW']")
    )
