# Standard module
import logging
import logging.config
from argparse import ArgumentParser

# Local
from crmprtd.download import ftp_download
from crmprtd import logging_args, setup_logging, common_auth_arguments

log = logging.getLogger(__name__)


def main():
    parser = ArgumentParser()
    parser = logging_args(parser)
    parser = common_auth_arguments(parser)
    parser.add_argument('-f', '--ftp_server',
                        default='BCFireweatherFTPp1.nrs.gov.bc.ca',
                        help=('Full uri to Wildfire Management Branch\'s ftp '
                              'server'))
    parser.add_argument('-F', '--ftp_file',
                        default='HourlyWeatherAllFields_WA.txt',
                        help=('Filename to open on the Wildfire Management '
                              'Branch\'s ftp site'))
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.wmb')

    ftp_download(args.username, args.password, args.auth_fname, args.auth_key,
                 args.ftp_server, args.ftp_file)


if __name__ == "__main__":
    main()
