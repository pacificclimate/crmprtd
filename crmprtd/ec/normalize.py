#!/usr/bin/env python

# Standard module
import sys
import logging
import pytz

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lxml.etree import parse, XSLT
from dateutil.parser import parse as dateparse

# Local
from pkg_resources import resource_stream
from crmprtd import Row

ns = {
    'om': 'http://www.opengis.net/om/1.0',
    'mpo': "http://dms.ec.gc.ca/schema/point-observation/2.1",
    'gml': "http://www.opengis.net/gml",
    'xlink': "http://www.w3.org/1999/xlink",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}


def parse_xml(file):
    # Parse and transform the xml
    et = parse(file)
    xsl = resource_stream('crmprtd', 'data/ec_xform.xsl')
    transform = XSLT(parse(xsl))
    return transform(et)


def normalize(file_stream):
    log = logging.getLogger(__name__)
    et = parse_xml(file_stream)

    members = et.xpath('//om:member', namespaces=ns)

    for member in members:
        om = OmMember(member)
        vars = om.observed_vars()

        for var in vars:
            try:
                ele = om.member.xpath(
                        "./om:Observation/om:result//mpo:element[@name='%s']" %
                        var, namespaces=ns)[0]
                val = float(ele.get('value'))
            # This shouldn't every be empty based on our xpath for selecting elements,
            # however I think that it _could_ be non-numeric and still be valid XML
            except ValueError as e:
                log.error('Unable to convert value, val:{}'.format(ele.get('value')))
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
                log.debug('Found station info', extra={'station_name': stn_name,
                                                       'station_id': native_id,
                                                       'lon': lon,
                                                       'lat': lat,
                                                       'time': obs_time})
            # An IndexError here means that the member has no station_name or
            # climate_station_number (or identification-elements), lat/lon, or obs_time
            # in which case we don't need to process this item
            except IndexError:
                log.warning("This member does not appear to be a station")


            tz = pytz.timezone('Canada/Pacific')
            try:
                date = dateparse(obs_time).replace(tzinfo=tz)
            except ValueError as e:
                raise e # FIXME: handle to error with logging when its setup

            named_row = Row(time=date,
                val=val,
                variable_name=var,
                unit=om.member_unit(var),
                network_name='EC',
                station_id=native_id,
                lat=lat,
                lon=lon)

            yield named_row


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
