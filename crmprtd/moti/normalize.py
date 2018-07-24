#!/usr/bin/env python

# Standard module
import pytz
import logging
from io import BytesIO

# Installed libraries
from pkg_resources import resource_filename
from lxml.etree import XSLT, parse as xmlparse
from dateutil.parser import parse as dateparse

# Local
from crmprtd import Row


xsl = resource_filename('crmprtd', 'data/moti.xsl')
transform = XSLT(xmlparse(xsl))
ns = {
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}
log = logging.getLogger(__name__)


def normalize(file_stream):
    log.info('Starting MOTI data normalization')
    et = xmlparse(file_stream)
    et = transform(et)

    obs_series = et.xpath("//observation-series")
    for series in obs_series:
        try:
            stn_id = series.xpath(
                        "./origin/id[@type='client']")[0].text.strip()
        except IndexError as e:
            raise Exception(
                "Could not detect the station id: xpath search "
                "'//observation-series/origin/id[@type='client']' return no "
                "results")

        members = series.xpath('./observation', namespaces=ns)
        for member in members:
            # get time and convert to datetime
            time = member.get('valid-time')
            if not time:
                log.warning("Could not find a valid-time attribute for this "
                            "observation")
                continue

            tz = pytz.timezone('Canada/Pacific')
            try:
                date = dateparse(time).replace(tzinfo=tz)
            except ValueError as e:
                log.error('Unable to convert value to datetime',
                          extra={'date': date})

            for obs in member.iterchildren():
                variable_name = obs.get('type')
                if variable_name is None:
                    continue

                try:
                    value_element = obs.xpath('./value')[0]
                except IndexError as e:
                    log.warning("Could not find the actual value for "
                                "observation. xpath search './value' "
                                "returned no results",
                                extra={'variable_name': variable_name})
                    continue

                try:
                    value = float(value_element.text)
                except ValueError:
                    log.error("Could not convert value to a number. "
                              "Skipping this observation.",
                              extra={'value': value})
                    continue

                yield Row(time=date,
                          val=value,
                          variable_name=variable_name,
                          unit=value_element.get('units'),
                          network_name='MOTI',
                          station_id=stn_id,
                          lat=None,
                          lon=None)
