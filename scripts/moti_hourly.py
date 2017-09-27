#!/usr/bin/env python

# Standard module
import os, sys
import logging, logging.config
from datetime import datetime, timedelta
from argparse import ArgumentParser
import requests
from traceback import print_exc
from pkg_resources import resource_stream

# Installed libraries
from lxml.etree import LxmlSyntaxError
from lxml.etree import parse
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd import retry
from crmprtd.moti import makeurl, process

# debug
from pdb import set_trace

def main(args):
    # Setup logging
    log_conf = yaml.load(args.log_conf)
    if args.log:
        log_conf['handlers']['file']['filename'] = args.log
    else:
        args.log = log_conf['handlers']['file']['filename']
    if args.error_email:
        log_conf['handlers']['mail']['toaddrs'] = args.error_email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger('crmprtd.moti')
    if args.log_level:
        log.setLevel(args.log_level)
    log.info('Starting MOTIe rtd')

    # Pull auth from file or command line
    if args.bciduser or args.bcidpass:
        auth = (args.bciduser, args.bcidpass)
    else:
        assert args.auth and args.auth_key, "Must provide both the auth file and the key to use for this script (--auth_key)"
        with open(args.auth, 'r') as f:
            config = yaml.load(f)
        auth = (config[args.auth_key]['username'], config[args.auth_key]['password'])

    auto = True
    try:
        if args.filename:
            log.debug("Opening local xml file {0} for reading".format(args.filename))
            auto = False
            fname = args.filename
            xml_file = open(args.filename, 'r')
            log.debug("File opened sucessfully")

        else:
            if args.start_time and args.end_time:
                args.start_time = datetime.strptime(args.start_time, '%Y/%m/%d %H:%M:%S')
                args.end_time = datetime.strptime(args.end_time, '%Y/%m/%d %H:%M:%S')
                log.info("Starting manual run using timestamps {0} {1}".format(args.start_time, args.end_time))
                assert args.end_time - args.start_time <= timedelta(7) # Requests of longer than 7 days not allowed by MoTI
                auto = False
            else:
                deltat = timedelta(1) # go back a day
                args.start_time = datetime.utcnow() - deltat
                args.end_time = datetime.utcnow()
                log.info("Starting automatic run using timestamps {0} {1}".format(args.start_time, args.end_time))

            if args.station_id:
                fmt = '%Y-%m-%d/%H'
                payload = {'request': 'historic', 'station': args.station_id, 'from': args.start_time, 'to':args.end_time}
            else:
                payload = {}

            fname = xml_file = os.path.join(args.cache_dir, 'moti-sawr7110_' + datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S') + '.xml')
            
            # Configure requests to use retry
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('https://', a)
            req = s.get('https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110', params=payload, auth=auth)
            
            log.info('{}: {}'.format(req.status_code, req.url))
            if req.status_code != 200:
                raise IOError("HTTP {} error for {}".format(req.status_code, req.url))
            with open(fname, 'wb') as f:
                f.write(req.content)
    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)

    Session = sessionmaker(create_engine(args.connection_string))
    sesh = Session()
    sesh.begin_nested()
    try:
        et = parse(xml_file)
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

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-c', '--connection_string', 
                        help='PostgreSQL connection string of form:\n\tdialect+driver://username:password@host:port/database\nExamples:\n\tpostgresql://scott:tiger@localhost/mydatabase\n\tpostgresql+psycopg2://scott:tiger@localhost/mydatabase\n\tpostgresql+pg8000://scott:tiger@localhost/mydatabase')
    parser.add_argument('-y', '--log_conf',
                        default = resource_stream('crmprtd', '/data/logging.yaml'),
                        help='YAML file to use to override the default logging configuration')
    parser.add_argument('-l', '--log', help="log filename")
    parser.add_argument('-e', '--error_email', 
                        help='e-mail address to which the program should report error which require human intervention')
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.  Note that debug output by default goes directly to file')
    parser.add_argument('-C', '--cache_dir', required = True,
                        help='directory in which to put the downloaded file in the event of a post-download error')
    parser.add_argument('-f', '--filename',
                        help='MPO-XML file to process')
    parser.add_argument('-S', '--start_time',
                        help="Alternate time to use for downloading (interpreted with strptime(format='Y/m/d H:M:S')")
    parser.add_argument('-E', '--end_time',
                        help="Alternate time to use for downloading (interpreted with strptime(format='Y/m/d H:M:S')")
    parser.add_argument('-i', '--station_id',
                        help="Station ID for which to download data")
    parser.add_argument('--auth', help="Yaml file with plaintext usernames/passwords")
    parser.add_argument('--auth_key', help="Top level key which user/pass are stored in yaml file.")
    parser.add_argument('--bciduser', help="The BCID username for data requests. Overrides auth file.")
    parser.add_argument('--bcidpass', help="The BCID password for data requests. Overrides auth file.")
    parser.add_argument('-D', '--diag', action="store_true", default = False,
                        help="Turn on diagnostic mode (no commits)")
    # parser.add_argument('-o', '--output_dir', dest='output_dir', help='directory in which to put the downloaded file')

    args = parser.parse_args()
    main(args)
