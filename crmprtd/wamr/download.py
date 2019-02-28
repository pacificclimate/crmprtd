import logging
from argparse import ArgumentParser

# Local
from crmprtd.download import ftp_download
from crmprtd import logging_args, setup_logging


log = logging.getLogger(__name__)


def main():
    parser = ArgumentParser()
    parser.add_argument('-f', '--ftp_server',
                        default='ftp.env.gov.bc.ca',
                        help=('Full hostname of Water and Air Monitoring and '
                              'Reporting\'s ftp server'))
    parser.add_argument('-F', '--ftp_dir',
                        default=('pub/outgoing/AIR/Hourly_Raw_Air_Data/'
                                 'Meteorological/'),
                        help='FTP Directory containing WAMR\'s data files')
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.wamr')

    ftp_path = '{}/{}'.format(args.ftp_server, args.ftp_dir)
    ftp_download(ftp_path, use_tls=False)


if __name__ == "__main__":
    main()
