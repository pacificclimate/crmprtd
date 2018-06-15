# Standard module
import sys
import os
import csv

from datetime import datetime

# Local
from crmprtd.wmb import ObsProcessor, DataLogger

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
        log.critical('''Error with Database connection
                        See logfile at {log}
                        Data saved at {d}
                     '''.format(log=args.log, d=data_archive), exc_info=True)
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
        log.critical('''Error data preprocessing.
                        See logfile at {log}
                        Data saved at {d}
                     '''.format(log=args.log, d=data_archive), exc_info=True)
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()
