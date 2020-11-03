'''Downloads meteorological data from Environment and Climate Change Canada.

Environment and Climate Change Canada (ECCC) post two sets of XML
files containing weather observations, one for daily variables
(e.g. daily high temperature) and one for hourly variables. They post
a new file every hour or day, depending on the temporal resolution.
Each new file containing only the data for that time range. Only the
previous month's worth of data is available.

It is recommended to run this script once per hour with the "-F
hourly" flag or once per day with the "-F daily" flag. There is
sufficient overlap between the time resolution and the historical data
available that only the most severe outtages (over a month) would
result in data loss.
'''

# Standard module
import sys
import logging
import logging.config
from datetime import datetime, timedelta
from argparse import ArgumentParser

# Local
from crmprtd.ec import makeurl
from crmprtd import setup_logging, logging_args
from crmprtd.download import https_download

log = logging.getLogger(__name__)


def download(time, frequency, province, language, baseurl):
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

        # Construct and download the xml
        url = makeurl(frequency, province, language, time, baseurl)

        scheme, _ = url.split(':', 1)
        https_download(url, scheme, log)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)


def main():
    desc = globals()['__doc__']
    parser = ArgumentParser(description=desc)
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
                              "format=YYYY/MM/DD HH:MM:SS)."
                              "Defaults to the previous hour/day (depending on"
                              " --frequency)."))
    parser.add_argument('-T', '--threshold', default=1000,
                        help=('Distance threshold (in meters) to use when '
                              'matching stations. Stations are considered a '
                              'match if they have the same id, name, and are '
                              'within this threshold'))
    parser.add_argument('-b', '--baseurl', default='https://dd.weather.gc.ca',
                        help=('Base URL (scheme and hostname components) for'
                              'the meteorological observations service'))
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.ec')

    download(args.time, args.frequency, args.province, args.language,
             args.baseurl)


if __name__ == "__main__":
    main()
