# Standard module
import sys
import logging

# debug

# Local
from crmprtd.wmb import ObsProcessor, DataLogger

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def prepare(args, log, data):
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
        log.critical('''Error with Database connection
                            See logfile at {l}
                            Data saved at {d}
                            '''.format(l = args.log, d = data_archive), exc_info=True)
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
                            See logfile at {l}
                            Data saved at {d}
                            '''.format(l = args.log, d = data_archive), exc_info=True)
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()
