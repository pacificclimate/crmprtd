# Standard module
import pytz
import logging

# Installed libraries
from lxml.etree import parse, XSLT
from dateutil.parser import parse as dateparse

# Local
from pkg_resources import resource_stream
from crmprtd import Row
from crmprtd.networks.ec import ns, OmMember, no_ns_element
from crmprtd.networks.ec_swob.download import split_multi_xml_stream


log = logging.getLogger(__name__)


def parse_xml(stream):

    with resource_stream("crmprtd", "data/ec_xform.xsl") as xsl:
        xsl = parse(xsl)

    # Parse and transform the xml
    et = parse(stream)
    transform = XSLT(xsl)
    return transform(et)


def identity(x):
    return x


def normalize(
    file_stream,
    network_name,
    station_id_attr="climate_station_number",
    station_id_xform=identity,
):
    for xml_file in split_multi_xml_stream(file_stream):
        yield from normalize_xml(
            xml_file, network_name, station_id_attr, station_id_xform
        )


def normalize_xml(
    file_stream,
    network_name,
    station_id_attr="climate_station_number",
    station_id_xform=identity,
):
    et = parse_xml(file_stream)

    members = et.xpath("//om:member", namespaces=ns)
    log.info("Starting %s data normalization", network_name)

    for member in members:
        om = OmMember(member)
        vars = om.observed_vars()

        for var in vars:
            try:
                ele = om.member.xpath(
                    "./om:Observation/om:result//"
                    "{}[@name='{}']".format(no_ns_element("element"), var),
                    namespaces=ns,
                )[0]
                val = ele.get("value")
                # Ignore missing values. We don't record them.
                if val == "MSNG":
                    log.debug("Ignoring missing obs with value 'MSNG'")
                    continue
                val = float(val)
            # This shouldn't ever be empty based on our xpath for selecting
            # elements, however it could be non-numeric and
            # still be valid XML
            except ValueError as e:
                log.error("Unable to convert value", extra={"val": (ele.get("value"))})
                continue

            try:
                log.debug("Finding Station attributes")
                station_id = member.xpath(
                    ".//{}/{}[@name='{}']".format(
                        no_ns_element("identification-elements"),
                        no_ns_element("element"),
                        station_id_attr,
                    ),
                    namespaces=ns,
                )[0].get("value")
                station_id = station_id_xform(station_id)

                lat, lon = map(
                    float, member.xpath(".//gml:pos", namespaces=ns)[0].text.split()
                )
                obs_time = member.xpath(
                    "./om:Observation/om:samplingTime//gml:timePosition", namespaces=ns
                )[0].text
                log.debug(
                    "Found station info",
                    extra={
                        "station_id": station_id,
                        "lon": lon,
                        "lat": lat,
                        "time": obs_time,
                    },
                )
            # An IndexError here means that the member has no station_name or
            # climate_station_number (or identification-elements), lat/lon,
            # or obs_time in which case we don't need to process this item
            except IndexError:
                log.warning("This member does not appear to be a station")
                continue

            try:
                date = dateparse(obs_time).astimezone(pytz.utc)
            except ValueError as e:
                log.error("Unable to parse date", extra={"exception": e})
                continue

            yield Row(
                time=date,
                val=val,
                variable_name=var,
                unit=om.member_unit(var),
                network_name=network_name,
                station_id=station_id,
                lat=lat,
                lon=lon,
            )
