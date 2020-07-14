# Standard libraries
import logging
import re
import csv

# Installed libraries
import pytz
from dateutil.parser import parse

# Local
from crmprtd import Row


log = logging.getLogger(__name__)


def normalize(file_stream):
    log.info('Starting WAMR data normalization')

    reader = csv.DictReader(file_stream.getvalue().decode('utf-8')
                            .splitlines())
    for row in reader:
        keys_of_interest = ('DATE_PST', 'STATION_NAME', 'UNIT',
                            'PARAMETER', 'REPORTED_VALUE')
        time, station_id, unit, variable_name, val = (
            row[k] for k in keys_of_interest)

        # skip over empty values
        if not val:
            continue

        try:
            value = float(val)
        except ValueError:
            log.error('Unable to convert val to float',
                      extra={'value': val})
            continue

        try:
            tz = pytz.timezone('Canada/Pacific')
            # Timezone information is not available from the text
            # string provided. However, the date field in WAMR's feed
            # is always titled "DATE_PST" (even during times of
            # DST). There's not really enough information available
            # from the network, so we'll have to assume that this
            # covers it.
            dt = tz.localize(parse(time)).astimezone(pytz.utc)
        except ValueError:
            log.error('Unable to convert date string to datetime',
                      extra={'time': time})
            continue

        substitutions = [
            ('% RH', '%'),
            ('\u00b0C', 'celsius'),
            ('mb', 'millibar'),
        ]
        for src, dest in substitutions:
            if unit == src:
                unit = re.sub(src, dest, unit)

        yield Row(time=dt,
                  val=value,
                  variable_name=variable_name,
                  unit=unit,
                  network_name='ENV-AQN',
                  station_id=station_id,
                  lat=None,
                  lon=None)
