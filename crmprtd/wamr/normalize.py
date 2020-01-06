# Installed libraries
import pytz
import logging
import itertools
from dateutil.parser import parse
import re

# Local
from crmprtd import Row


log = logging.getLogger(__name__)


def normalize(file_stream):
    log.info('Starting WAMR data normalization')

    for row in itertools.islice(file_stream, 1, None):
        row = row.decode('utf-8')
        try:
            time, station_id, _, variable_name, \
                _, _, _, unit, _, _, _, val = row.strip().split(',')
        except ValueError as e:
            log.error('Unable to retrieve items.',
                      extra={'exception': e, 'row': row})
            continue

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
