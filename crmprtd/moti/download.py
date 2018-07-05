#!/usr/bin/env python

# Standard module
import os
import sys
import logging
import logging.config
from datetime import datetime, timedelta
import requests

# Installed libraries
import yaml

# Local
from crmprtd.moti.normalize import prepare


def logging_setup(log_conf, log, error_email, log_level):
    log_c = yaml.load(log_conf)
    if log:
        log_c['handlers']['file']['filename'] = log
    else:
        log = log_c['handlers']['file']['filename']
    if error_email:
        log_c['handlers']['mail']['toaddrs'] = error_email
    logging.config.dictConfig(log_c)
    log = logging.getLogger('crmprtd.moti')
    if log_level:
        log.setLevel(log_level)

    return log


def download(payload, auth, fname, log):
    # Configure requests to use retry
    s = requests.Session()
    a = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount('https://', a)
    req = s.get('https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110',
                params=payload, auth=auth)

    log.info('{}: {}'.format(req.status_code, req.url))
    if req.status_code != 200:
        raise IOError("HTTP {} error for {}".format(req.status_code, req.url))
    with open(fname, 'wb') as f:
        f.write(req.content)

    return fname


def run(args):
    # Setup logging
    log = logging_setup(args.log_conf, args.log,
                        args.error_email, args.log_level)
    log.info('Starting MOTIe rtd')

    # Pull auth from file or command line
    if args.bciduser or args.bcidpass:
        auth = (args.bciduser, args.bcidpass)
    else:
        assert args.auth and args.auth_key, ("Must provide both the auth file "
                                             "and the key to use for this "
                                             "script (--auth_key)")
        with open(args.auth, 'r') as f:
            config = yaml.load(f)
        auth = (config[args.auth_key]['username'],
                config[args.auth_key]['password'])

    try:
        if args.filename:
            log.info("Opening local xml file for reading",
                     extra={'file': args.filename})
            fname = args.filename
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

            fname = os.path.join(
                    args.cache_dir, 'moti-sawr7110_' +
                    datetime.strftime(datetime.now(), '%Y-%m-%dT%H-%M-%S') +
                    '.xml')
            fname = download(payload, auth, fname, log)
            prepare(args, log, fname)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)
