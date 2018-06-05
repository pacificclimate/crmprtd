#!/usr/bin/env python

# Standard module
import sys
import logging

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.ec import ObsProcessor, parse_xml


def ec_normalize(args, log, fname):
    # Wrap critical secion
    try:
        log.info("Parsing input xml")
        et = parse_xml(fname)   # is this part of normalize or align?

        # there should be no database code in -NORMALIZE- portion of pipeline
        log.info("Creating database session")
        Session = sessionmaker(create_engine(args.connection_string))
        sesh = Session()

    except Exception as e:
        log.critical("Critical errors have occured in the EC real time downloader. Log file %s. Data archive %s" % (args.log, fname), exc_info=True)
        sys.exit(1)

    try:
        ### BEGIN NESTED ###
        sesh.begin_nested()
        log.info("Starting observation processing")
        op = ObsProcessor(et, sesh, args.threshold)
        op.process()
        log.info("Done processing observations")
        if args.diag:
            log.info('Diagnostic mode, rolling back all transactions')
            sesh.rollback()
        else:
            log.info('Commiting the session')
            sesh.commit()
        ### END BEGIN NESTED ###

    except Exception as e:
        sesh.rollback()
        log.critical("Critical errors have occured in the EC real time downloader. Log file %s. Data archive %s" % (args.log, fname), exc_info=True)
        sys.exit(1)

    finally:
        sesh.commit()
        sesh.close()
