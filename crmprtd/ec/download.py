# Standard module
import sys
import logging
import logging.config
from datetime import datetime, timedelta
from argparse import ArgumentParser
import pickle

# Installed libraries
import requests

# Local
from crmprtd.ec import makeurl
from crmprtd import setup_logging, logging_args

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

        pickle.dump('Network module name: ec', sys.stdout.buffer)
        for line in req.iter_content(chunk_size=None):
            pickle.dump(line, sys.stdout.buffer)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--province', required=True,
                        help='2 letter province code')
    parser.add_argument('-g', '--language', default='e',
                        choices=['e', 'f'],
                        help="'e' (english) | 'f' (french)")
    parser.add_argument('-F', '--frequency', required=True,
                        choices=['daily', 'hourly'],
                        help='daily|hourly')
    parser.add_argument('-t', '--time',
                        help=("Alternate *UTC* time to use for downloading "
                              "(interpreted using "
                              "format=YYYY/MM/DD HH:MM:SS)"))
    parser.add_argument('-T', '--threshold', default=1000,
                        help=('Distance threshold to use when matching '
                              'stations.  Stations are considered a match if '
                              'they have the same id, name, and are within '
                              'this threshold'))
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.ec')

    download(args.time, args.frequency, args.province, args.language)
