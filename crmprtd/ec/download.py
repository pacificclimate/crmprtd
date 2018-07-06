# Standard module
import sys
import logging
import logging.config
from datetime import datetime, timedelta
from tempfile import SpooledTemporaryFile

# Installed libraries
import requests
import logging

# Local
from crmprtd.ec import makeurl


def download(args):
    # Setup logging
    log = logging.getLogger(__name__)
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

        with SpooledTemporaryFile(max_size=2048, mode='r+b') as tempfile:
            tempfile.write(req.content)

            tempfile.seek(0)
            yield tempfile

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)
