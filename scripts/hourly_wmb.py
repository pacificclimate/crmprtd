#!/usr/bin/env python

# From Jim Colley <Jim.Colley@gov.bc.ca>
# "The first file contains a rolling 24hrs of data for each station, and is
# updated at approximately 00:35 past each hour"
#
# FIXME: Replace opts.log with native python logging configuration
# FIMXE: Replace email_error with using a logging handler to catch critical
# errors (i.e. logger.critical()) and do the email

from pkg_resources import resource_stream
from argparse import ArgumentParser
from itertools import tee

# Local
from crmprtd.wmb.download import download
from crmprtd.wmb.normalize import normalize
from crmprtd.wmb import setup_logging
from crmprtd import common_script_arguments

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--ftp_server',
                        default='BCFireweatherFTPp1.nrs.gov.bc.ca',
                        help=('Full uri to Wildfire Management Branch\'s ftp '
                              'server'))
    parser.add_argument('-F', '--ftp_file',
                        default='HourlyWeatherAllFields_WA.txt',
                        help=('Filename to open on the Wildfire Management '
                              'Branch\'s ftp site'))
    parser.add_argument('--auth',
                        help="Yaml file with plaintext usernames/passwords")
    parser.add_argument('--auth_key',
                        help=("Top level key which user/pass are stored in "
                              "yaml file."))
    parser.add_argument('--username',
                        help=("The username for data requests. Overrides auth "
                              "file."))
    parser.add_argument('--password',
                        help=("The password for data requests. Overrides auth "
                              "file."))
    parser.add_argument('-a', '--archive_dir',
                        help=('Directory in which to put data that could not '
                              'be added to the database'))
    parser = common_script_arguments(parser)
    args = parser.parse_args()
    log = setup_logging(args.log_level, args.log, args.error_email)

    download_iter = download(args)

    if args.cache_file:
        download_iter, cache_iter = tee(download_iter)
        with open(args.cache_file, 'w') as f:
            for chunk in cache_iter:
                f.write(chunk)

    for row in normalize(download_iter):
        print(row)
