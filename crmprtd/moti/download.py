#!/usr/bin/env python

# Standard module
import sys
import logging
import logging.config
from datetime import datetime, timedelta

# Installed libraries
import requests

# Local
from crmprtd.download import extract_auth

log = logging.getLogger(__name__)


def download(username, password, auth, auth_key,
             start_time, end_time, station_id):
    log.info('Starting MOTIe rtd')

    try:
        auth = extract_auth(username, password, auth, auth_key)

        if start_time and end_time:
            start_time = datetime.strptime(
                start_time, '%Y/%m/%d %H:%M:%S')
            end_time = datetime.strptime(
                end_time, '%Y/%m/%d %H:%M:%S')
            log.info("Starting manual run using timestamps {0} {1}".format(
                start_time, end_time))
            # Requests of longer than 7 days not allowed by MoTI
            assert end_time - start_time <= timedelta(7)
        else:
            deltat = timedelta(1)  # go back a day
            start_time = datetime.utcnow() - deltat
            end_time = datetime.utcnow()
            log.info("Starting automatic run "
                     "using timestamps {0} {1}".format(start_time,
                                                       end_time))

        if station_id:
            payload = {'request': 'historic', 'station': station_id,
                       'from': start_time, 'to': end_time}
        else:
            payload = {}

        # Configure requests to use retry
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('https://', a)
        req = s.get('https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110',
                    params=payload, auth=(auth['u'], auth['p']))

        log.info('{}: {}'.format(req.status_code, req.url))
        if req.status_code != 200:
            raise IOError(
                "HTTP {} error for {}".format(req.status_code, req.url))

        return req.iter_content(chunk_size=None)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)
