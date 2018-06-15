import sys

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.wamr import rows2db
from crmprtd.wamr import file2rows


def input_file_prepare(args, error_file, log):
    with open(args.input_file) as f:
        rows, fieldnames = file2rows(f, log)
    log.info('{0} observations read into memory'.format(len(rows)))
    prepare(rows, error_file, log, args)


def prepare(rows, error_file, log, args):
    # Database connection
    try:
        engine = create_engine(args.connection_string)
        Session = sessionmaker(engine)
        sesh = Session()
    except Exception as e:
        log.critical('Error with Database connection', exc_info=True)
        sys.exit(1)

    # Hand the row off to the database processings/insertion part of the script
    rows2db(sesh, rows, error_file, log, args.diag)
