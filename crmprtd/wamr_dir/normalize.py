import sys
import csv
import logging
import os

from datetime import datetime
from argparse import ArgumentParser
from pkg_resources import resource_stream

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.wamr import rows2db
from crmprtd.wamr import file2rows, ftp2rows


def wamr_normalize(rows, error_file, log, args):
    # Database connection
    try:
        engine = create_engine(args.connection_string)
        Session = sessionmaker(engine)
        sesh = Session()
    except Exception as e:
        log.critical('Error with Database connection', exc_info=True)
        sys.exit(1)

    # Hand the row off to the database processings/insertion part of the script
    # should this be a part of normalize?
    rows2db(sesh, rows, error_file, log, args.diag)
