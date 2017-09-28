#!/usr/bin/env python

# Standard module
import os, sys
import logging, logging.config
from datetime import datetime, timedelta
from argparse import ArgumentParser
from pkg_resources import resource_filename

# Installed libraries
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from psycopg2 import InterfaceError
import yaml

# Local
from crmprtd.ec import makeurl, ObsProcessor, parse_xml, extract_fname_from_url

def main(args):
    # Setup logging
    with open(args.log_conf, 'rb') as f:
        log_conf = yaml.load(f)
    if args.log:
        log_conf['handlers']['file']['filename'] = args.log
    else:
        args.log = log_conf['handlers']['file']['filename']
    if args.error_email:
        log_conf['handlers']['mail']['toaddrs'] = args.error_email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger('crmprtd.ec')
    if args.log_level:
        log.setLevel(args.log_level)

    log.info('Starting EC rtd')

    try:
        if args.filename:
            log.debug("Opening local xml file %s for reading", args.filename)
            fname = args.filename
            # Just test that we *can* open the file. Don't catch exception here
            _ = open(args.filename, 'r')
            log.debug("File opened sucessfully")
        else:

            # Determine time parameter
            if args.time:
                args.time = datetime.strptime(args.time, '%Y/%m/%d %H:%M:%S')
                log.info("Starting manual run using timestamp %s", args.time)
            else:
                deltat = timedelta(1/24.) if args.frequency == 'hourly' else timedelta(1) # go back a day
                args.time = datetime.utcnow() - deltat
                log.info("Starting automatic run using timestamp %s", args.time)

            # Configure requests to use retry
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('https://', a)

            # Construct and download the xml
            url = makeurl(args.frequency, args.province, args.language, args.time)
            fname = os.path.join(args.cache_dir, extract_fname_from_url(url))

            log.info("Downloading %s", url)
            req = s.get(url)
            if req.status_code != 200:
                raise IOError("HTTP {} error for {}".format(req.status_code, req.url))

            log.info("Saving data to %s", fname)
            with open(fname, 'wb') as f:
                f.write(req.content)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)

    # Wrap critical secion
    try:
        log.info("Parsing input xml")
        et = parse_xml(fname)

        log.info("Creating database session")
        Session = sessionmaker(create_engine(args.connection_string))
        sesh = Session()

    except Exception:
        log.critical("Critical errors have occured in the EC real time downloader. Log file %s. Data archive %s", args.log, fname, exc_info=True)
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

    except Exception:
        sesh.rollback()
        log.critical("Critical errors have occured in the EC real time downloader. Log file %s. Data archive %s", args.log, fname, exc_info=True)
        sys.exit(1)

    finally:
        sesh.commit()
        sesh.close()

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-c', '--connection_string', required=True,
                         help='PostgreSQL connection string of form:\n\tdialect+driver://username:password@host:port/database\nExamples:\n\tpostgresql://scott:tiger@localhost/mydatabase\n\tpostgresql+psycopg2://scott:tiger@localhost/mydatabase\n\tpostgresql+pg8000://scott:tiger@localhost/mydatabase')
    parser.add_argument('-y', '--log_conf',
                         default=resource_filename('crmprtd', '/data/logging.yaml'),
                         help='YAML file to use to override the default logging configuration')
    parser.add_argument('-l', '--log',
                         help="log filename")
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.  Note that debug output by default goes directly to file')
    parser.add_argument('-e', '--error_email',
                        help='e-mail address to which the program should report error which require human intervention')
    parser.add_argument('-C', '--cache_dir', required=True,
                        help='directory in which to put the downloaded file in the event of a post-download error')
    parser.add_argument('-f', '--filename',
                        help='MPO-XML file to process')
    parser.add_argument('-p', '--province',  required=True,
                        help='2 letter province code')
    parser.add_argument('-L', '--language', default='e',
                        choices=['e', 'f'],
                        help="'e' (english) | 'f' (french)")
    parser.add_argument('-F', '--frequency', required=True,
                        choices=['daily', 'hourly'],
                        help='daily|hourly')
    parser.add_argument('-t', '--time',
                        help="Alternate *UTC* time to use for downloading (interpreted using format=YYYY/MM/DD HH:MM:SS)")
    parser.add_argument('-T', '--threshold', default=1000,
                        help='Distance threshold to use when matching stations.  Stations are considered a match if they have the same id, name, and are within this threshold')
    parser.add_argument('-D', '--diag', default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")

    args = parser.parse_args()
    main(args)
