#!/usr/bin/env python

# Standard module
import pytz
import logging

# Installed libraries
from pkg_resources import resource_filename
from lxml.etree import XSLT, parse as xmlparse
from dateutilr import parse as dateparse

# Local
from crmprtd import Row


xsl = resource_filename('crmprtd', 'data/moti.xsl')
transform = XSLT(xmlparse(xsl))
ns = {
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}


def normalize(file_stream):
    log = logging.getLogger(__name__)
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
                raise e  # FIXME: handle to error with logging when its setup

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
                                extra={'variable_name': variable_name}
                    continue

                unit = value_element.get('units')

                try:
                    value = float(value_element.text)
                except ValueError:
                    log.warning("Could not convert value to a number. "
                                "Skipping this observation.",
                                extra={'value': value})
                    continue

                named_row = Row(time=date,
                                val=value,
                                variable_name=variable_name,
                                unit=unit,
                                network_name='MOTI',
                                station_id=stn_id,
                                lat=None,
                                lon=None)

                yield named_row
