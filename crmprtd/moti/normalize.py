#!/usr/bin/env python

# Standard module
import sys

# Installed libraries
from lxml.etree import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.moti import process


def prepare(args, log, infile):
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
        log.critical('Serious errros with MOTIe rtd, see logs',
                     extra={'log': args.log})
        sys.exit(1)
    finally:
        sesh.commit()
