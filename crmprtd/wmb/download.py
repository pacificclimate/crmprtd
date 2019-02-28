# Standard module
import logging
from argparse import ArgumentParser

# Local
from crmprtd.download import extract_auth, ftp_download
from crmprtd import logging_args, setup_logging, common_auth_arguments

log = logging.getLogger(__name__)


def main():
    parser = ArgumentParser()
    parser = logging_args(parser)
    parser = common_auth_arguments(parser)
    parser.add_argument('-f', '--ftp_path',
                        default='BCFireweatherFTPp1.nrs.gov.bc.ca/',
                        help=('Full uri to Wildfire Management Branch\'s ftp '
                              'directory'))
    parser.add_argument('-F', '--ftp_file',
                        default='HourlyWeatherAllFields_WA.txt',
                        help=('Filename to open on the Wildfire Management '
                              'Branch\'s ftp site'))
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.wmb')

    auth = extract_auth(args.username, args.password, args.auth_fname,
                        args.auth_key)

    ftp_download(args.ftp_path, args.ftp_file, auth=auth, use_tls=True)


if __name__ == "__main__":
    main()
