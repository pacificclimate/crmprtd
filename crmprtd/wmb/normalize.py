# Installed libraries
import pytz
import logging
import itertools
from dateutil.parser import parse

# Local
from crmprtd import Row


def normalize(file_stream):
    log = logging.getLogger(__name__)

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
            # check values to ensure valid row
            if key == 'station_id' or key == 'weather_date':
                continue

            elif len(value) == 0:
                continue

            # parse date
            date = d['weather_date']
            parsed_date = '{}-{}-{} '.format(date[:4], date[4:6], date[6:8])
            if date[8:10] == '24':
                parsed_date += '00:00'
            else:
                parsed_date += '{}:00'.format(date[8:10])

            # convert types where necessary
            tz = pytz.timezone('Canada/Pacific')
            try:
                cleaned_date = parse(parsed_date).replace(tzinfo=tz)
            except ValueError:
                log.error('Unable to parse date {}'.format(date))
                continue

            try:
                val = float(value)
            except ValueError:
                log.error('Unable to convert val: {} to float'.format(value))
                continue

            # create namedTuple
            named_row = Row(time=cleaned_date,
                            val=val,
                            variable_name=key,
                            unit=None,
                            network_name='WMB',
                            station_id=d['station_code'],
                            lat=None,
                            lon=None)

            yield named_row
