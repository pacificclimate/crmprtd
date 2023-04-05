# Standard library
import json

# Installed libraries
import pytz
import logging
from datetime import datetime

# Local
from crmprtd import Row


log = logging.getLogger(__name__)


def normalize(stream):
    log.info("Starting CRD data normalization")

    tz = pytz.timezone("Canada/Pacific")

    data = json.load(stream)

    units = data["HEADER"]["_units"]
    var_names = [unit.replace("Unit", "") for unit in units.keys()]
    log.debug("Found variables %s", var_names)

    for record in data["DATA"]:
        # Timezone information isn't provided by CRD, but the
        # observations appear to be in local time. The max time
        # value found in a request is the most recent hour local
        # time. Hopefully assuming this will suffice.
        date = datetime.strptime(record["DateTimeString"], "%Y%m%d%H%M%S")
        date = tz.localize(date).astimezone(pytz.utc)

        for var_name in var_names:
            # CRD uses -9999 and null for missing values. Skip these.
            # See page 2 here: https://tinyurl.com/quczs93
            val = record[var_name]
            if val is None or val == -9999:
                continue

            yield Row(
                time=date,
                val=val,
                variable_name=var_name,
                unit=units[f"{var_name}Unit"],
                network_name="CRD",
                station_id=record["StationName"],
                lat=None,
                lon=None,
            )
