import sys
import csv

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from collections import namedtuple

# Local
from crmprtd.wamr import rows2db


def normalize_ftp(ftpreader, error_file, args, log=None):
    # Just store the lines in memory
    # It's non-ideal but neither classes support coroutine send/yield
    if not log:
        log = logging.getLogger('__name__')
    lines = []

    def callback(line):
        lines.append(line)

    for filename in ftpreader.filenames:
        log.info("Downloading %s", filename)
        # FIXME: This line has some kind of race condition with this
        ftpreader.connection.retrlines('RETR {}'.format(filename), callback)

    r = csv.DictReader(lines)

    unnamed_rows = [tuple(line.split(',')) for index, line in enumerate(lines) if index != 0]
    named_rows = unnamed2named(unnamed_rows)

    store_file(args, r, len(unnamed_rows), log)

    for i, row in enumerate(named_rows):
        if i == 10:
            break
        print(row)
    # return named_rows???


def normalize_file(f, args, error_file, log):
    try:
        reader = csv.DictReader(f)
        unnamed_rows = [tuple(line.strip().split(',')) for index, line in enumerate(f) if index != 0]
    except csv.Error as e:
        log.critical('Unable to load data from local file', exc_info=True)
        sys.exit(1)
    except Exception as e:
        log.error('An error has occured while converting file to rows')
        raise e

    named_rows = unnamed2named(unnamed_rows)

    log.info('{0} observations read into memory'.format(len(named_rows)))

    for i, row in enumerate(named_rows):
        if i == 10:
            break
        print(row)
    # return named_rows???


def unnamed2named(unnamed_rows):
    Row = namedtuple('Row', "date_pst ems_id station_name parameter air_parameter instrument raw_value unit status aircodestatus status_description reported_value")

    # named tuple
    named_rows = [Row(date_pst=line[0],
                      ems_id=line[1],
                      station_name=line[2],
                      parameter=line[3],
                      air_parameter=line[4],
                      instrument=line[5],
                      raw_value=line[6],
                      unit=line[7],
                      status=line[8],
                      aircodestatus=line[9],
                      status_description=line[10],
                      reported_value=line[11]) for line in unnamed_rows]

    return named_rows


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
