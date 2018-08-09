#!/usr/bin/env python

# Standard module
import os
import sys
from datetime import datetime, timedelta
from argparse import ArgumentParser
import requests
import logging

# Installed libraries
from lxml.etree import parse
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.moti import process
from crmprtd import setup_logging, common_script_arguments, \
    common_auth_arguments


def main(args):
    log = logging.getLogger('crmprtd.moti')
    log.info('Starting MOTIe rtd')

    # Pull auth from file or command line
    if args.bciduser or args.bcidpass:
        auth = (args.bciduser, args.bcidpass)
    else:
        assert args.auth_fname and args.auth_key, ("Must provide both the "
                                                   "auth file and the key to "
                                                   "use for this script "
                                                   "(--auth_key)")
        with open(args.auth_fname, 'r') as f:
            config = yaml.load(f)
        auth = (config[args.auth_key]['username'],
                config[args.auth_key]['password'])

    try:
        if args.input_file:
            log.info("Opening local xml file for reading",
                     extra={'filae': args.input_file})
            fname = args.input_file
            xml_file = open(args.input_file, 'r')
            log.debug("File opened sucessfully")

        else:
            if args.start_time and args.end_time:
                args.start_time = datetime.strptime(
                    args.start_time, '%Y/%m/%d %H:%M:%S')
                args.end_time = datetime.strptime(
                        args.end_time, '%Y/%m/%d %H:%M:%S')
                log.info('Starting manual run using timestamps',
                         extra={'start_time': args.start_time,
                                'end_time': args.end_time})
                # Requests of longer than 7 days not allowed by MoTI
                assert args.end_time - args.start_time <= timedelta(7)
            else:
                deltat = timedelta(1)  # go back a day
                args.start_time = datetime.utcnow() - deltat
                args.end_time = datetime.utcnow()
                log.info('Starting automatic run using timestamps',
                         extra={'start_time': args.start_time,
                                'end_time': args.end_time})

            if args.station_id:
                payload = {'request': 'historic', 'station': args.station_id,
                           'from': args.start_time, 'to': args.end_time}
            else:
                payload = {}

            fname = xml_file = os.path.join(
                args.cache_dir, 'moti-sawr7110_' +
                datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S') +
                '.xml')

            # Configure requests to use retry
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('https://', a)
            req = s.get('https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110',
                        params=payload, auth=auth)

            log.info('Status', extra={'status_code': req.status_code,
                                      'url': req.url})
            if req.status_code != 200:
                raise IOError("HTTP {} error for {}".format(
                    req.status_code, req.url))
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
        log.critical('Serious errros with MOTIe rtd, see logs',
                     extra={'log': args.log_filename})
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-S', '--start_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')"))
    parser.add_argument('-E', '--end_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')"))
    parser.add_argument('-s', '--station_id',
                        help="Station ID for which to download data")
    parser.add_argument('--bciduser',
                        help=("The BCID username for data requests. Overrides "
                              "auth file."))
    parser.add_argument('--bcidpass',
                        help=("The BCID password for data requests. Overrides "
                              "auth file."))
    parser = common_script_arguments(parser)
    parser = common_auth_arguments(parser)
    args = parser.parse_args()
    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.moti')
    main(args)
