# Standard module
import sys
import logging
import logging.config
from argparse import ArgumentParser
from itertools import islice

# Installed libraries
import requests

# Local
from crmprtd import setup_logging, logging_args

log = logging.getLogger(__name__)


def download(url_base, url_dir, station):
    log.info('Starting download for ENV-ASP network')

    try:
        # Configure requests to use retry
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('https://', a)

        url = '{}{}/{}.csv'.format(url_base, url_dir, station)

        log.info("Downloading {0}".format(url))
        req = s.get(url)
        if req.status_code != 200:
            raise IOError(
                "HTTP {} error for {}".format(req.status_code, req.url))

        lines = req.iter_lines(decode_unicode=True)
        header = next(islice(lines, 0, 1))
        rest = islice(lines, 1, None)

        print('native_id,'+header)
        # sys.stdout.buffer.write(b'native_id,'+header)

        for line in rest:
            # Prepend the native_id to the line since it's not included
            # in the data
            line = '{},{}'.format(station, line)
            # line = station.encode('utf-8') + b',' + line + b'\n'
            print(line)
            # sys.stdout.buffer.write(line)

    except IOError:
        log.exception("Failed to download")
        sys.exit(1)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '-b', '--url_base',
        help='Base part of the resource URL (scheme+host)',
        default='http://bcrfc.env.gov.bc.ca'
    )
    parser.add_argument(
        '-d', '--url_dir',
        help='Directory path of the resource URL',
        default='/data/asp/realtime/data'
    )
    parser.add_argument(
        '-s', '--station',
        help='Native ID of the station to download (e.g. 1A01P)'
    )
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.asp')

    download(args.url_base, args.url_dir, args.station)


if __name__ == "__main__":
    main()
