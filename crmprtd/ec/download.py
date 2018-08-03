# Standard module
import sys
import logging
import logging.config
from datetime import datetime, timedelta

# Installed libraries
import requests

# Local
from crmprtd.ec import makeurl

log = logging.getLogger(__name__)


def download(time, frequency, province, language):
    log.info('Starting EC rtd')

    try:
        # Determine time parameter
        if time:
            time = datetime.strptime(time, '%Y/%m/%d %H:%M:%S')
            log.info("Starting manual run "
                     "using timestamp {0}".format(time))
        else:
            # go back a day
            deltat = timedelta(
                1 / 24.) if frequency == 'hourly' else timedelta(1)
            time = datetime.utcnow() - deltat
            log.info("Starting automatic run "
                     "using timestamp {0}".format(time))

        # Configure requests to use retry
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('https://', a)

        # Construct and download the xml
        url = makeurl(frequency, province, language, time)

        log.info("Downloading {0}".format(url))
        req = s.get(url)
        if req.status_code != 200:
            raise IOError(
                "HTTP {} error for {}".format(req.status_code, req.url))
        return req.iter_content(chunk_size=None)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)
