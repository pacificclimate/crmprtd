'''Downloads met data from the BC Capital Regional District (CRD)

The CRD operates a network of automated weather and hydrology stations
in the Greater Victoria Water Supply Area. The default data request
returns all data for the past 28 days. Theorettically, any date range
which does not exceed 28 days, can also be requested and downloaded.

It is recommended to run this script once per one or two weeks to
collect all available data (plus, presumably some duplicate data from
the last run). If the script is run less than once per month, you will
miss data.
'''

import sys
from argparse import ArgumentParser
import logging


import crmprtd.download
from crmprtd import logging_args, setup_logging

log = logging.getLogger(__name__)


def make_url(client_id, sdate=None, edate=None):
    return f"https://webservices.crd.bc.ca/weatherdata/{client_id}/"


def download(client_id, start_date, end_date):
    url = make_url(client_id, start_date, end_date)
    try:
        crmprtd.download.https_download(url, 'https', log)

    except IOError:
        log.exception("Unable to download or open JSON data")
        sys.exit(1)


def main():  # pragma: no cover
    desc = globals()['__doc__']
    parser = ArgumentParser(description=desc)
    parser = logging_args(parser)
    parser.add_argument('-c', '--client_id',
                        help=("Mandatory client ID provided by CRD"))
    # parser.add_argument('-S', '--start_time',
    #                     help=("Alternate time to use for downloading "
    #                           "(interpreted with "
    #                           "strptime(format='Y/m/d H:M:S'). "
    #                           "Defaults to one hour prior to now"))
    # parser.add_argument('-E', '--end_time',
    #                     help=("Alternate time to use for downloading "
    #                           "(interpreted with "
    #                           "strptime(format='Y/m/d H:M:S'). "
    #                           "Defaults to now."))
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.crd')

    download(args.client_id, None, None)


if __name__ == "__main__":
    main()
