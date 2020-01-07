'''Downloads the BC Ministry of Transportation and Infrastructure (MoTI) data.

The BC Ministry of Transportation and Infrastructure, Avalache Safety
Program network has an application which returns meteorological data
upon request. By default the application returns all data available
from the previous hour. It *is* possible to request any data, however
the time range is limited to 7 days and you need to explicitly limit
the query to a specific station id. I.e. you cannot specify a time
range without a priori information. Also see:
https://github.com/pacificclimate/crmprtd/issues/52.

It is recommend to run this script, time parameter free every hour to
collect the bulk of the data. It is further recommended to do an
additional run once per one or two weeks with the aid of a station
list to fill in any gaps that may have arisen from outages or data
that came in late. Gaps can be filled in at any time, so there is
little risk of missing data.
'''


# Standard module
import sys
import logging
import logging.config
from warnings import warn
from datetime import datetime, timedelta
from argparse import ArgumentParser

# Local
from crmprtd.download import extract_auth, https_download
from crmprtd import common_auth_arguments, logging_args, setup_logging

log = logging.getLogger(__name__)


def verify_date(datestring, default, label='start_time'):
    try:
        return datetime.strptime(datestring, '%Y/%m/%d %H:%M:%S')
    except (ValueError, TypeError):
        warn(
            'Parameter {} \'{}\' is undefined or unparseable. Using the '
            'default \'{}\''.format(label, datestring, default)
        )
        return default


def download(username, password, auth_fname, auth_key,
             start_time, end_time, station_id):
    log.info('Starting MOTIe rtd')

    auth_yaml = open(auth_fname, 'r').read() if auth_fname else None
    auth = extract_auth(username, password, auth_yaml, auth_key)

    if start_time or end_time:
        if not station_id:
            raise ValueError(
                "MOTI's SAWR service only allows the user to specify a time "
                "range for an individual station. Please either specify a "
                "station id (-s) or omit the time arguments")

        now = datetime.datetime.utcnow()
        start_time = verify_date(
            start_time, now - timedelta(days=0, seconds=60), 'start_time')
        end_time = verify_date(end_time, now, 'end_time')

        log.info("Starting manual run using timestamps {0} {1}".format(
            start_time, end_time))

        request_length = end_time - start_time
        if request_length > timedelta(7):
            raise ValueError(
                "You requested a data for {}, however requests longer than 7 "
                "days are not permitted by MoTI's SAWR service"
                .format(request_length))

        payload = {'request': 'historic', 'station': station_id,
                   'from': start_time, 'to': end_time}
    else:
        log.info("Starting an automatic run to MOTI's SAWR service")
        payload = {}

    url = 'https://prdoas2.apps.th.gov.bc.ca/saw-data/sawr7110'

    try:
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
                              "strptime(format='Y/m/d H:M:S'). "
                              "Defaults to one hour prior to now"))
    parser.add_argument('-E', '--end_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S'). "
                              "Defaults to now."))
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
