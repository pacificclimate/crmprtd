#!/usr/bin/env python

# Standard module
import os, sys
import logging, logging.config
from datetime import datetime, timedelta
from argparse import ArgumentParser
from urllib import urlopen
from traceback import print_exc
from pkg_resources import resource_filename

# Installed libraries
from psycopg2 import InterfaceError, ProgrammingError, OperationalError
from lxml.etree import LxmlSyntaxError
import yaml

# Local
from crmprtd.ec import makeurl, ObsProcessor

# debug
from pdb import set_trace

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
    log = logging.getLogger('crmprtd.wmb')
    log.info('Starting WMB rtd')
    if args.log_level:
        log.setLevel(args.log_level)

    auto = True
    try:
        if args.filename:
            logging.debug("Opening local xml file {0} for reading".format(args.filename))
            auto = False
            fname = args.filename
            xml_file = open(args.filename, 'r')
            logging.debug("File opened sucessfully")
        else:
            if args.time:
                args.time = datetime.strptime(args.time, '%Y/%m/%d %H:%M:%S')
                logging.info("Starting manual run using timestamp {0}".format(args.time))
                auto = False
            else:
                deltat = timedelta(1/24.) if args.frequency == 'hourly' else timedelta(1) # go back a day
                args.time = datetime.utcnow() - deltat
                logging.info("Starting automatic run using timestamp {0}".format(args.time))
            url = makeurl(args.frequency, args.province, args.language, args.time)
            fname = url['filename']
            logging.info("Downloading {0}".format(url['url']))
            xml_file = urlopen(url['url'])
            if xml_file.getcode() == 404: raise IOError("HTTP 404 error for %s" % url['url'])
    except IOError:
        logging.exception("Unable to download or open xml data")
        sys.exit(1)

    # instantiate the ObsProcessor (do the startup stuff, like opening db connection and parsing the XML)
    try:
        logging.info("Instantiating the ObsProcessor",)
        op = ObsProcessor(xml_file, args)
        logging.info("Done setting up ObsProcessor")
    except (LxmlSyntaxError, IOError, OperationalError), e:
        if type(e) == OperationalError:
            logging.exception("Could not connect to database")
        if type(e) == LxmlSyntaxError:
            logging.exception("Failed to parse xml file \n {0}".format(xml_file))
        if type(e) == IOError:
            logging.exception("Failed to open xml file\n{0}".format(xml_file))
        # Save data for reprosessing
        if auto:
            fname = os.path.join(args.cache_dir, 'failure-' + fname)
        else:
            fname = os.path.join(args.cache_dir, 'manual_run_' + datetime.now().strftime('%Y%m%dT%H%M%S') + '_failure-' + fname)
        logging.info("Saving data at: {}".format(fname))
        f = open(fname, 'w')
        f.write(xml_file.read())
        logging.info("Done saving data")
        logging.critical('''Critical errors have occured in the EC real time downloader that require a human touch.
        The daemon was unable to either download, open, or parse the incoming xml and no observations could be inserted.
        Please consult the log file at {log}.
        Data has been archived at {f}.'''.format(log=args.log, f=fname))
        sys.exit(1)

    # process the XML and do the db insertions
    try:
        logging.info("Starting to process observations")
        op.process()
        logging.info("Done processing observations")
    except (InterfaceError, ProgrammingError, Exception), e:
        logging.exception("Unhandleable exception, saving remaining XML file {} for further examination".format(fname))
    finally:
        if auto:
            remainder = os.path.join(args.cache_dir, 'remainder-' + fname)
        else:
            remainder = os.path.join(args.cache_dir, 'manual_run_' + datetime.now().strftime('%Y%m%dT%H%M%S') + '_remainder-' + fname)
        op.save(remainder)
        logging.info("Data saved at {}".format(remainder))

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
    parser.add_argument('-T', '--threshold', dest='thresh', default=1000,
                        help='Distance threshold to use when matching stations.  Stations are considered a match if they have the same id, name, and are within this threshold')
    parser.add_argument('-D', '--diag', default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")

    args = parser.parse_args()
    main(args)
