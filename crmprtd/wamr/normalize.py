import csv
import sys

# Installed libraries
from datetime import datetime
import pytz
import logging
from dateutil.parser import parse

# Local
from crmprtd.wamr import setup_logging
from crmprtd import Row


def normalize(file_stream):
    log = logging.getLogger(__name__)
    tz = pytz.timezone('Canada/Pacific')

    is_first = True
    for row in file_stream.readlines():
        cleaned = row.strip().split(',')
        if is_first:
            is_first = False
            continue

        try:
            named_row = Row(time=parse(cleaned[0]).replace(
                tzinfo=tz),
                val=float(cleaned[11]),
                variable_name=cleaned[3],
                unit=cleaned[7],
                network_name='WAMR',
                station_id=cleaned[1],
                lat=None,
                lon=None)
            yield named_row
        except Exception as e:
            log.error('Unable to process row: {}'.format(row))
