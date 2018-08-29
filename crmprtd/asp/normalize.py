# Standard library
import re
import logging

# Installed libraries
import pytz
from dateutil.parser import parse

# Local
from crmprtd import Row


log = logging.getLogger(__name__)


def extract_units(vars):
    '''Take a set of varname/unit strings in the format of "Variable (unit)"
       and separate them out
    '''
    rv = []
    pattern = re.compile(r'(\S+) \((\S+)\)')
    for string in vars:
        match = pattern.match(string)
        if match:
            rv.append(match.groups())
        else:
            rv.append((string, None))
    return rv


def normalize(file_stream):
    log.info('Starting ENV-ASP data normalization')

    def clean_row(row):
        return row.strip().replace('"', '').split(',')

    # set variable names and units using first row in file stream
    var_names = []
    for first_row in file_stream:
        first_row = first_row.decode('utf-8')
        for var in clean_row(first_row):
            var_names.append(var)
        break

    var_names, units = zip(*extract_units(var_names))

    for row in file_stream:
        row = row.decode('utf-8')
        # assign variable name to value
        data = [(var_name, unit, value)
                for var_name, unit, value in
                zip(var_names, units, clean_row(row))]

        # extract station_id and weather_date from list
        _, _, station_id = data.pop(0)
        data.pop(0)  # Station name
        _, _, weather_date = data.pop(0)

        tz = pytz.timezone('UTC')
        try:
            date = parse(weather_date).replace(tzinfo=tz)
        except ValueError:
            log.error('Unable to convert date', extra={'date': weather_date})
            continue

        for var_name, unit, value in data:

            # skip if value string is empty
            if not value:
                continue

            try:
                value = float(value)
            except ValueError:
                log.error('Unable to convert val to float',
                          extra={'value': value})
                continue

            if unit == 'C':
                unit = 'celsius'

            yield Row(time=date,
                      val=value,
                      variable_name=var_name,
                      unit=unit,
                      network_name='ENV-ASP',
                      station_id=station_id,
                      lat=None,
                      lon=None)
