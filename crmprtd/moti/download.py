#!/usr/bin/env python

# Standard module
import sys
import os
import logging
import logging.config
from datetime import datetime, timedelta
from tempfile import SpooledTemporaryFile
import requests

# Installed libraries
import yaml


log = logging.getLogger(__name__)


def download(args):
    log.info('Starting MOTIe rtd')

    try:
        # Pull auth from file or command line
        if args.bciduser or args.bcidpass:
            auth = (args.bciduser, args.bcidpass)
        else:
            assert args.auth and args.auth_key, ("Must provide both the auth "
                                                 "file and the key to use for "
                                                 "this script (--auth_key)")
            with open(args.auth, 'r') as f:
                config = yaml.load(f)
            auth = (config[args.auth_key]['username'],
                    config[args.auth_key]['password'])

        if args.start_time and args.end_time:
            args.start_time = datetime.strptime(
                args.start_time, '%Y/%m/%d %H:%M:%S')
            args.end_time = datetime.strptime(
                args.end_time, '%Y/%m/%d %H:%M:%S')
            log.info("Starting manual run using timestamps {0} {1}".format(
                args.start_time, args.end_time))
            # Requests of longer than 7 days not allowed by MoTI
            assert args.end_time - args.start_time <= timedelta(7)
        else:
            deltat = timedelta(1)  # go back a day
            args.start_time = datetime.utcnow() - deltat
            args.end_time = datetime.utcnow()
            log.info("Starting automatic run "
                     "using timestamps {0} {1}".format(args.start_time,
                                                       args.end_time))

        if args.station_id:
            payload = {'request': 'historic', 'station': args.station_id,
                       'from': args.start_time, 'to': args.end_time}
        else:
            payload = {}

        # Configure requests to use retry
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('https://', a)
        req = s.get('https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110',
                    params=payload, auth=auth)

        log.info('{}: {}'.format(req.status_code, req.url))
        if req.status_code != 200:
            raise IOError(
                "HTTP {} error for {}".format(req.status_code, req.url))

        yield req.iter_content(chunk_size=2**20)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)
