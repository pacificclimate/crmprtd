# Installed libraries
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

    var_names = ['station_code',
                 'weather_date',
                 'precipitation',
                 'temperature',
                 'relative_humidity',
                 'wind_speed',
                 'wind_direction',
                 'ffmc',
                 'isi',
                 'fwi',
                 'rn_1_pluvio1',
                 'snow_depth',
                 'snow_depth_quality',
                 'precip_pluvio1_status',
                 'precip_pluvio1_total',
                 'rn_1_pluvio2',
                 'precip_pluvio2_status',
                 'precip_pluvio2_total',
                 'rn_1_RIT',
                 'precip_RIT_Status',
                 'precip_RIT_total',
                 'precip_rgt',
                 'solar_radiation_LICOR',
                 'solar_radiation_CM3']

    for row in itertools.islice(file_stream, 1, None):
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
