# Installed libraries
import sys
import pytz
import logging
import itertools
from dateutil.parser import parse
import datetime

from collections import OrderedDict

# Local
from crmprtd import Row


log = logging.getLogger(__name__)


def normalize(file_stream):
    log.info('Starting WMB data normalization')

    def clean_row(row):
        return row.strip().replace('"', '').split(',')

    # set variable names using first row in file stream
    var_names = []
    for first_row in file_stream:
        for var in clean_row(first_row):
            var_names.append(var)
        break

    for row in file_stream:
        # assign variable name to value
        data = [(var_name, value) for var_name, value in zip(var_names, clean_row(row))]

        # extract station_id and weather_date from list
        _, station_id = data.pop(0)
        _, weather_date = data.pop(0)

        tz = pytz.timezone('Canada/Pacific')
        try:
            date = datetime.datetime.strptime(weather_date, "%Y%m%d%H").replace(tzinfo=tz)
        except ValueError:
            log.error('Unable to convert date', extra={'date': weather_date})
            continue

        for pair in data:
            var_name, value = pair

            # skip if value string is empty
            if not value:
                continue

            try:
                value = float(value)
            except ValueError:
                log.error('Unable to convert val to float',
                          extra={'value': value})
                continue

            yield Row(time=date,
                      val=value,
                      variable_name=var_name,
                      unit=None,
                      network_name='WMB',
                      station_id=station_id,
                      lat=None,
                      lon=None)
