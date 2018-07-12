# Installed libraries
import sys
import pytz
import logging
import itertools
from dateutil.parser import parse
import datetime

# Local
from crmprtd import Row


def normalize(file_stream):
    log = logging.getLogger(__name__)
    log.info('Starting WMB data normalization')

    var_names = []
    is_first = True
    # be sure to grap variable names on first iteration
    for row in file_stream:
        if is_first:
            for var in row.strip().replace('"', '').split(','):
                var_names.append(var)

            is_first = False
            continue

        # assign variable name to value
        d = {val: item
             for val, item in zip(var_names,
                                  row.strip().replace('"', '').split(','))}

        for key, value in d.items():
            # we do not need to create a separate row for these values
            if key == 'station_id' or key == 'weather_date':
                continue

            # skip is there is no value
            elif value is None:
                continue

            # convert types where necessary
            date = d['weather_date']
            tz = pytz.timezone('Canada/Pacific')
            try:
                cleaned_date = datetime.datetime.strptime('{}-{}-{} {}'.format(date[:4], date[4:6], date[6:8], date[8:10]), "%Y-%m-%d %H").replace(tzinfo=tz)
            except ValueError:
                log.error('Unable to parse date', extra={'date': date})
                continue

            try:
                val = float(value)
            except ValueError:
                log.error('Unable to convert val to float',
                          extra={'value': value})
                continue

            # create namedTuple
            yield Row(time=cleaned_date,
                      val=val,
                      variable_name=key,
                      unit=None,
                      network_name='WMB',
                      station_id=d['station_code'],
                      lat=None,
                      lon=None)
