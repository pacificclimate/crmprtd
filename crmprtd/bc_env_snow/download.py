# Standard module
import datetime
import logging
from argparse import ArgumentParser

# Local
from crmprtd.ec_swob.download import download
from crmprtd import logging_args, setup_logging

log = logging.getLogger(__name__)


def main():
    parser = ArgumentParser()
    parser = logging_args(parser)
    parser.add_argument('-d', '--date',
                        help=("Alternate date to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')"))
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.bc-env-snow')

    if not args.date:
        dl_date = datetime.datetime.now()
    else:
        dl_date = datetime.datetime.strptime(args.date, '%Y/%m/%d %H:%M:%S')

    download(
        'https://dd.weather.gc.ca/observations/swob-ml/partners/'
        'bc-env-snow/', dl_date
    )


if __name__ == "__main__":
    main()
