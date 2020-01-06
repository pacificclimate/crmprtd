# Installed libraries
import pytz
import logging
from datetime import datetime

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
        first_row = first_row.decode('utf-8')
        for var in clean_row(first_row):
            var_names.append(var)
        break

    for row in file_stream:
        row = row.decode('utf-8')
        # assign variable name to value
        data = [(var_name, value)
                for var_name, value in zip(var_names, clean_row(row))]

        # extract station_id and weather_date from list
        _, station_id = data.pop(0)
        _, weather_date = data.pop(0)

        tz = pytz.timezone('Canada/Pacific')
        # The date's provided are in 1-24 hour format *roll*
        hour = int(weather_date[-2:]) - 1
        weather_date = weather_date[:-2] + str(hour)
        try:
            # Timezone information isn't provided by WMB, but the
            # observations appear to be in local time. The max time
            # value found in a request is the most recent hour local
            # time. Hopefully assuming this will suffice.
            date = datetime.strptime(weather_date, "%Y%m%d%H")
            date = tz.localize(date).astimezone(pytz.utc)
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
                      network_name='FLNRO-WMB',
                      station_id=station_id,
                      lat=None,
                      lon=None)
