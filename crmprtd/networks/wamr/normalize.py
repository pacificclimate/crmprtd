# Standard libraries
import io
import logging
import re
import csv
from pkg_resources import resource_stream

# Installed libraries
import pytz
from dateutil.parser import parse
import yaml

# Local
from crmprtd import Row


log = logging.getLogger(__name__)


def get_one_of(elements):
    for e in elements:
        # FIXME: Condition should probably be `e is not None`
        if e:
            return e
    # FIXME: {e} should probably be {elements}
    raise ValueError(f"No elements of {e} have a truthy value")


def normalize(file_stream):
    log.info("Starting WAMR data normalization")

    # There is a set of Metro Vancouver's stations that are being
    # delivered to us by WAMR, but it is desired that they are re-
    # associated with the correct network. Attempting this by altering the
    # normalization to the correct station_id and the correct network
    # name. Issue here is that the metrovan variables need to match the ENV-AQN
    # variables. Will work on that in the database.

    station_substitutions_fp = "networks/wamr/station_substitutions.yaml"
    try:
        with resource_stream("crmprtd", station_substitutions_fp) as f:
            station_substitutions = yaml.safe_load(f)
    except FileNotFoundError:
        log.error(
            f"Cannot open resource file '{station_substitutions_fp}'. "
            f"Normalization cannot proceed."
        )
        return

    string_stream = io.StringIO(file_stream.read().decode("utf-8"))
    reader = csv.DictReader(string_stream)
    for row in reader:
        keys_of_interest = (
            "DATE_PST",
            "EMS_ID",
            "STATION_NAME",
            "UNIT",
            "UNITS",
            "PARAMETER",
            "REPORTED_VALUE",
            "RAW_VALUE",
            "LONGITUDE",
            "LATITUDE",
        )
        (
            time,
            ems_id,
            station_name,
            unit,
            units,
            variable_name,
            rep_val,
            raw_val,
            lon,
            lat,
        ) = (row[k] if k in row else None for k in keys_of_interest)

        # Circa 2020, BC ENV is presenting inconsistent names for
        # several of their columns (UNIT/UNITS, EMS_ID/STATION_NAME,
        # REPORTED_VALUE/RAW_VALUE/ROUNDED_VALUE. Ensure that we have
        # at least one of these sets.
        unit = get_one_of((unit, units))
        reported_station_id = get_one_of((ems_id, station_name))
        try:
            val = get_one_of((rep_val, raw_val))
        except ValueError:
            # skip over empty values
            log.warning("Unable to get value from row", extra={"row": row})
            continue

        try:
            value = float(val)
        except ValueError:
            log.error("Unable to convert val to float", extra={"value": val})
            continue

        try:
            tz = pytz.timezone("Canada/Pacific")
            # Timezone information is not available from the text
            # string provided. However, the date field in WAMR's feed
            # is always titled "DATE_PST" (even during times of
            # DST). There's not really enough information available
            # from the network, so we'll have to assume that this
            # covers it.
            dt = tz.localize(parse(time)).astimezone(pytz.utc)
        except ValueError:
            log.error("Unable to convert date string to datetime", extra={"time": time})
            continue

        variable_substitutions = [
            ("% RH", "%"),
            ("\u00b0C", "celsius"),
            ("mb", "millibar"),
        ]
        for src, dest in variable_substitutions:
            if unit == src:
                unit = re.sub(src, dest, unit)

        if reported_station_id in station_substitutions:
            station_id = station_substitutions[reported_station_id]
            network_name = "MVan"
        else:
            station_id = reported_station_id
            network_name = "ENV-AQN"

        yield Row(
            time=dt,
            val=value,
            variable_name=variable_name,
            unit=unit,
            network_name=network_name,
            station_id=station_id,
            lat=lat,
            lon=lon,
        )
