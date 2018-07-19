#!/usr/bin/env python

# Standard module
import logging
import pytz
from io import BytesIO

# Installed libraries
from lxml.etree import parse, XSLT, fromstring
from dateutil.parser import parse as dateparse

# Local
from pkg_resources import resource_stream
from crmprtd import Row
from crmprtd.ec import ns, OmMember


log = logging.getLogger(__name__)


def parse_xml(file):
    # Parse and transform the xml
    et = parse(file)
    xsl = resource_stream('crmprtd', 'data/ec_xform.xsl')
    transform = XSLT(parse(xsl))
    return transform(et)


def normalize(file_stream):
    et = parse_xml(BytesIO(file_stream))

    members = et.xpath('//om:member', namespaces=ns)
    log.info('Starting EC data normalization')

    for member in members:
        om = OmMember(member)
        vars = om.observed_vars()

        for var in vars:
            try:
                ele = om.member.xpath(
                        "./om:Observation/om:result//mpo:element[@name='%s']" %
                        var, namespaces=ns)[0]
                val = float(ele.get('value'))
            # This shouldn't every be empty based on our xpath for selecting
            # elements, however I think that it _could_ be non-numeric and
            # still be valid XML
            except ValueError as e:
                log.error('Unable to convert value',
                          extra={'val': (ele.get('value'))})
                continue

            attrs = ['station_name', 'climate_station_number']
            try:
                log.debug("Finding Station attributes")
                stn_name, native_id = map(lambda x: member.xpath(
                    ".//mpo:identification-elements/mpo:element[@name='%s']" %
                    x, namespaces=ns)[0].get('value'), attrs)
                lat, lon = map(float, member.xpath(
                    './/gml:pos', namespaces=ns)[0].text.split())
                obs_time = member.xpath(
                    './om:Observation/om:samplingTime//gml:timePosition',
                    namespaces=ns)[0].text
                log.debug('Found station info',
                          extra={'station_name': stn_name,
                                 'station_id': native_id,
                                 'lon': lon,
                                 'lat': lat,
                                 'time': obs_time})
            # An IndexError here means that the member has no station_name or
            # climate_station_number (or identification-elements), lat/lon,
            # or obs_time in which case we don't need to process this item
            except IndexError:
                log.warning("This member does not appear to be a station")

            tz = pytz.timezone('Canada/Pacific')
            try:
                date = dateparse(obs_time).replace(tzinfo=tz)
            except ValueError as e:
                log.error('Unable to parse date', extra={'exception': e})

            yield Row(time=date,
                      val=val,
                      variable_name=var,
                      unit=om.member_unit(var),
                      network_name='EC',
                      station_id=native_id,
                      lat=lat,
                      lon=lon)
