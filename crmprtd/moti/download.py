'''Downloads the BC Ministry of Transportation and Infrastructure (MoTI) data.

The BC Ministry of Transportation and Infrastructure, Avalache Safety Program network


It is recommended to run this script once per one or two weeks to
collect all available data (plus, presumably some duplicate data from
the last run). If the script is run less than once per month, you will
miss data.
'''


# Standard module
import sys
import logging
import logging.config
from datetime import datetime, timedelta
from argparse import ArgumentParser

# Local
from crmprtd.download import extract_auth, https_download
from crmprtd import common_auth_arguments, logging_args, setup_logging

log = logging.getLogger(__name__)


def download(username, password, auth_fname, auth_key,
             start_time, end_time, station_id):
    log.info('Starting MOTIe rtd')

    try:
        auth_yaml = open(auth_fname, 'r').read() if auth_fname else None
        auth = extract_auth(username, password, auth_yaml, auth_key)

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

        url = 'https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110'
        https_download(url, 'https', log, auth, payload)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)


def main():
    desc = globals()['__doc__']
    parser = ArgumentParser(description=desc)
    parser = logging_args(parser)
    parser = common_auth_arguments(parser)
    parser.add_argument('-S', '--start_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')"))
    parser.add_argument('-E', '--end_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')"))
    parser.add_argument('-s', '--station_id',
                        default=None,
                        help="Station ID for which to download data")
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.moti')

    download(args.username, args.password, args.auth_fname, args.auth_key,
             args.start_time, args.end_time, args.station_id)


if __name__ == "__main__":
    main()
