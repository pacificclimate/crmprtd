# Standard module
import sys
import os
import logging
import logging.config
from datetime import datetime, timedelta
from tempfile import SpooledTemporaryFile

# Installed libraries
import requests

# Local
from crmprtd.ec import makeurl


log = logging.getLogger(__name__)


def download(args):
    log.info('Starting EC rtd')

    try:
        # Determine time parameter
        if args.time:
            args.time = datetime.strptime(args.time, '%Y/%m/%d %H:%M:%S')
            log.info("Starting manual run "
                     "using timestamp {0}".format(args.time))
        else:
            # go back a day
            deltat = timedelta(
                1 / 24.) if args.frequency == 'hourly' else timedelta(1)
            args.time = datetime.utcnow() - deltat
            log.info("Starting automatic run "
                     "using timestamp {0}".format(args.time))

        # Configure requests to use retry
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('https://', a)

        # Construct and download the xml
        url = makeurl(args.frequency, args.province, args.language, args.time)

        log.info("Downloading {0}".format(url))
        req = s.get(url)
        if req.status_code != 200:
            raise IOError(
                "HTTP {} error for {}".format(req.status_code, req.url))

        yield req.iter_content(chunk_size=int(os.environ.get('CRMPRTD_MAX_CACHE', 2**20)))

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)
