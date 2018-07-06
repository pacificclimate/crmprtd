# Installed libraries
import pytz
import logging
import itertools
from dateutil.parser import parse

# Local
from crmprtd import Row


def normalize(file_stream):
    log = logging.getLogger(__name__)

    for row in itertools.islice(file_stream, 1, None):
        try:
            time, station_id, _, variable_name, \
                _, _, _, unit, _, _, _, val = row.strip().split(',')
        except ValueError as e:
            log.error('Unable to retrieve items. e:{}\n\t[{}]'.format(e, row))
            continue

        try:
            val = float(val)
        except ValueError:
            log.error('Unable to convert val: {} to float'.format(val))
            continue

        try:
            tz = pytz.timezone('Canada/Pacific')
            time = parse(time).replace(tzinfo=tz)
        except ValueError:
            log.error(
                'Unable to convert date string: {} to datetime'.format(time))
            continue

        named_row = Row(time=time,
                        val=val,
                        variable_name=variable_name,
                        unit=unit,
                        network_name='WAMR',
                        station_id=station_id,
                        lat=None,
                        lon=None)

        yield named_row
