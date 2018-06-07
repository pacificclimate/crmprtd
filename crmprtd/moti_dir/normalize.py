#!/usr/bin/env python

# Standard module
import sys
import logging

# Installed libraries
from lxml.etree import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.moti import process


def moti_normalize(args, log, infile):
    Session = sessionmaker(create_engine(args.connection_string))
    sesh = Session()
    sesh.begin_nested()
    try:
        et = parse(infile)
        r = process(sesh, et)
        log.info(r)
        if args.diag:
            log.info('Diagnostic mode, rolling back')
            sesh.rollback()
        else:
            log.info('Comitting session')
            sesh.commit()
    except Exception as e:
        sesh.rollback()
        log.critical('Serious errors with MOTIe rtd, see logs at {}'.format(args.log), exc_info=True)
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()