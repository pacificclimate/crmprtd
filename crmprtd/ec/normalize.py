#!/usr/bin/env python

# Standard module
import sys

# Installed libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.ec import ObsProcessor, parse_xml


def prepare(args, log, infile):
    # Wrap critical secion
    try:
        log.info("Parsing input xml")
        et = parse_xml(infile)

        log.info("Creating database session")
        Session = sessionmaker(create_engine(args.connection_string))
        sesh = Session()

    except Exception as e:
        log.critical('Critical errors have occured in the EC real time '
                     'downloader', extra={'log_file': args.log,
                                          'data_archive': infile})
        sys.exit(1)

    try:
        # BEGIN NESTED #
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
        # END BEGIN NESTED #

    except Exception as e:
        log.critical('Critical errors have occured in the EC real time '
                     'downloader', extra={'log_file': args.log,
                                          'data_archive': infile})
        sys.exit(1)

    finally:
        sesh.commit()
        sesh.close()