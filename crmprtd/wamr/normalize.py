# Installed libraries
import pytz
import logging
import itertools
from dateutil.parser import parse

# Local
from crmprtd import Row


log = logging.getLogger(__name__)


def normalize(file_stream):
    log.info('Starting WAMR data normalization')

    for row in itertools.islice(file_stream, 1, None):
        try:
            time, station_id, station_name, variable_name, \
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
            dt = parse(time).replace(tzinfo=tz)
        except ValueError:
            log.error('Unable to convert date string to datetime',
                      extra={'time': time})
            continue

        yield Row(time=dt,
                  val=value,
                  variable_name=variable_name,
                  unit=unit,
                  network_name='ENV-AQN',
                  station_name=station_name,
                  station_id=station_id,
                  lat=None,
                  lon=None)
