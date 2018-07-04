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


def save_file(reader, cache_dir, data):
    # save the downloaded file
    fname_out = os.path.join(cache_dir,
                             'wmb_download' +
                             datetime.strftime(datetime.now(),
                                               '%Y-%m-%dT%H-%M-%S') +
                             '.csv')
    with open(fname_out, 'w') as f_out:
        copier = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
        copier.writeheader()
        copier.writerows(data)


def prepare(args, log, reader):
    data = list(reader)
    save_file(reader, args.cache_dir, data)
    log.info('processed all rows from reader')
    log.info('{0} observations read into memory'.format(len(data)))

    dl = DataLogger()

    # Open database connection
    # I think this would fall under the align/insert?
    try:
        engine = create_engine(args.connection_string)
        Session = sessionmaker(engine)
        sesh = Session()
        sesh.begin_nested()
    except Exception as e:
        dl.add_row(data, 'db-connection error')
        data_archive = dl.archive(args.archive_dir)
        log.critical('Error with database connection, see logfile, data saved',
                     extra={'log': args.log, 'data_archive': data_archive})
        sys.exit(1)

    try:
        op = ObsProcessor(sesh, data, args)
        op.process()
        if args.diag:
            log.info('Diagnostic mode, rolling back all transactions')
            sesh.rollback()
        else:
            log.info('Commiting the session')
            sesh.commit()

    except Exception as e:
        dl.add_row(data, 'preproc error')
        sesh.rollback()
        data_archive = dl.archive(args.archive_dir)
        log.critical('Error with database connection, see logfile, data saved',
                     extra={'log': args.log, 'data_archive': data_archive})
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()
