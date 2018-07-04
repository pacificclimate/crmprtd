import csv
import sys

# Installed libraries
from datetime import datetime
import pytz
import logging
from dateutil.parser import parse

# Local
from crmprtd.wmb import setup_logging
from crmprtd import Row


def normalize(file_stream):
    log = logging.getLogger(__name__)
    tz = pytz.timezone('Canada/Pacific')

    is_first = True
    var_row = None
    for row in file_stream.readlines():
        cleaned = row.strip().replace('"', '').split(',')

        if is_first:
            is_first = False
            var_row = cleaned[2:]
            continue

        # loop through all variables
        for i,var in enumerate(var_row, 2):
            # check if var has value
            if len(cleaned[i]) == 0:
                continue

            # parse date
            date = cleaned[1]
            parsed_date = date[0:4] + '-' + date[4:6] + '-' + date[6:8] + ' '
            if date[8:10] == '24':
                parsed_date = parsed_date + '00'
            else:
                parsed_date = parsed_date + date[8:10]
            cleaned_date = parse(parsed_date).replace(tzinfo=tz)

            try:
                named_row = Row(time=cleaned_date,
                    val=float(cleaned[i]),
                    variable_name=var,
                    unit=None,
                    network_name='WMB',
                    station_id=cleaned[0],
                    lat=None,
                    lon=None)
                yield named_row
            except Exception as e:
                log.error('Unable to process row: {}'.format(row))
