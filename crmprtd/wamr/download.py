import ftplib
import logging
import os
import sys

from tempfile import SpooledTemporaryFile
from argparse import ArgumentParser

# Local
from crmprtd.download import retry, ftp_connect
from crmprtd.download import FTPReader
from crmprtd import logging_args, setup_logging


log = logging.getLogger(__name__)


def download_args(parser):
    parser.add_argument('-f', '--ftp_server',
                        default='ftp.env.gov.bc.ca',
                        help=('Full hostname of Water and Air Monitoring and '
                              'Reporting\'s ftp server'))
    parser.add_argument('-F', '--ftp_dir',
                        default=('pub/outgoing/AIR/Hourly_Raw_Air_Data/'
                                 'Meteorological/'),
                        help='FTP Directory containing WAMR\'s data files')
    parser.add_argument('--outfile',
                        default=None,
                        help='File where the ouput of download() will be '
                             'printed')
    return parser


def download(ftp_server, ftp_dir):
    '''Executes the first stage of the data processing pipeline.

       Downloads the data, according to the download arguments
       provided (generally from the command line) and outputs the data
       to stdout.
    '''
    log.info('Starting WAMR rtd')

    try:
        # Connect FTP server and retrieve file
        ftpreader = ftp_connect(WAMRFTPReader, ftp_server, ftp_dir,
                                log)

        with SpooledTemporaryFile(
                max_size=int(os.environ.get('CRMPRTD_MAX_CACHE', 2**20)),
                mode='r+') as tempfile:

            for filename in ftpreader.filenames:

                def callback(line):
                    tempfile.write('{}\n'.format(line))

                log.info("Downloading %s", filename)
                ftpreader.connection.retrlines('RETR {}'.format(filename),
                                               callback)

            tempfile.seek(0)

            # print module name for pipe
            print("Network module name: wamr")
            for line in tempfile.readlines():
                print(line.strip('\n'))
            sys.stdout.flush()

    except Exception:
        log.exception("Unable to process ftp")


class WAMRFTPReader(FTPReader):
    '''Glue between the FTP class methods (which are callback based)
       and the csv.DictReader class (which is iteration based)
    '''

    def __init__(self, host, user, password, data_path, log=None):
        self.filenames = []

        @retry(ftplib.error_temp, tries=4, delay=3, backoff=2, logger=log)
        def ftp_connect_with_retry(host, user, password):
            con = ftplib.FTP(host)
            con.login(user, password)
            return con

        self.connection = ftp_connect_with_retry(host, user, password)

        def callback(line):
            self.filenames.append(line)

        self.connection.retrlines('NLST ' + data_path, callback)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser = download_args(parser)
    parser = logging_args(parser)
    args = parser.parse_args()

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'crmprtd.wamr')

    download(args.ftp_server, args.ftp_dir)
