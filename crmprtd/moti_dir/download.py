#!/usr/bin/env python

# Standard module
import os, sys
import logging, logging.config
from datetime import datetime, timedelta
import requests

# Installed libraries
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.moti_dir.normalize import moti_normalize

# debug


def moti_download(args):
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
                from_ = from_.strftime(fmt)
                to = to.strftime(fmt)
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

    moti_normalize(args, log, xml_file)
