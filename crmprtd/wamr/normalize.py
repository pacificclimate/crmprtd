import sys
import csv

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from collections import namedtuple
import pytz
from dateutil.parser import parse

# Local
from crmprtd.wamr import rows2db
from crmprtd.wamr import setup_logging


# TODO: store_file needs to be changed to store rows
def normalize(file_stream):
    Row = namedtuple('Row', "date native_id station_name parameter unit data")
    tz = pytz.timezone('Canada/Pacific')

    log =setup_logging('INFO')
    for row in file_stream:
        cleaned = row.strip().split(',')

        try:
            named_row = Row(date=parse(cleaned[0]).replace(tzinfo=tz),
                      	    native_id=cleaned[1],
                      		station_name=cleaned[2],
                      		parameter=cleaned[3],
                      		unit=cleaned[7],
                      		data=float(cleaned[11]))
            yield named_row
        except Exception as e:
            log.warning('Unable to process row: {}'.format(row))


def store_file(args, dict, rows_len, log):
    if not args.cache_file:
            args.cache_file = 'wamr_download_{}.csv'.format(datetime.strftime(
                datetime.now(), '%Y-%m-%dT%H-%M-%S'))
    with open(args.cache_file, 'w') as cache_file:
        cache_rows(cache_file, dict, dict.fieldnames)

    log.info('{0} observations read into memory'.format(rows_len))

def cache_rows(file_, rows, fieldnames):
    copier = csv.DictWriter(file_, fieldnames=fieldnames)
    copier.writeheader()
    copier.writerows(rows)

# def prepare(rows, error_file, log, args):
#     # Database connection
#     try:
#         engine = create_engine(args.connection_string)
#         Session = sessionmaker(engine)
#         sesh = Session()
#     except Exception as e:
#         log.critical('Error with Database connection', exc_info=True)
#         sys.exit(1)
#
#
#     # Hand the row off to the database processings/insertion part of the script
#     rows2db(sesh, rows, error_file, log, args.diag)
