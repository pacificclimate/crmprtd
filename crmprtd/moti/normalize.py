#!/usr/bin/env python

# Standard module
import pytz
import logging

# Installed libraries
from pkg_resources import resource_filename
from lxml.etree import XSLT, parse as xmlparse
from dateutil.parser import parse as dateparse

# Local
from crmprtd import Row, iterable_to_stream


xsl = resource_filename('crmprtd', 'data/moti.xsl')
transform = XSLT(xmlparse(xsl))
ns = {
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}
log = logging.getLogger(__name__)


def normalize(iterable):
    log.info('Starting MOTI data normalization')
    file_stream = iterable_to_stream(iterable)
    et = xmlparse(file_stream)
    et = transform(et)
    obs_series = et.xpath("//observation-series")
    if not len(obs_series[0]):
        log.warning("Empty observation series: xpath search "
                    "'//observation-series' return no results")
        return
    for series in obs_series:
        try:
            stn_id = series.xpath(
                        "./origin/id[@type='client']")[0].text.strip()
        except IndexError as e:
            log.error("Could not detect the station id: xpath search "
                      "'//observation-series/origin/id[@type='client']' "
                      "return no results", extra={'exception': e})
            continue

        members = series.xpath('./observation', namespaces=ns)
        for member in members:
            # get time and convert to datetime
            time = member.get('valid-time')
            if not time:
                log.warning("Could not find a valid-time attribute for this "
                            "observation")
                continue

            try:
                # MoTI gives us an ISO formatted time string with
                # timezone info attached so it should be sufficient to
                # simply parse it and display it as UTC.
                date = dateparse(time).astimezone(pytz.utc)
            except ValueError as e:
                log.warning('Unable to convert value to datetime',
                            extra={'time': time})
                continue

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
                              extra={'value': value_element})
                    continue

                yield Row(time=date,
                          val=value,
                          variable_name=variable_name,
                          unit=value_element.get('units'),
                          network_name='MoTIe',
                          station_id=stn_id,
                          lat=None,
                          lon=None)
