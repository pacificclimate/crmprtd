#!/usr/bin/env python

'''
Script to download data from the BC Ministry of Environment Air Quality Branch

Water and Air Monitoring and Reporting? (WAMR)

This is largely lifted and modified from the hourly_wmb.py script
'''


from argparse import ArgumentParser
from itertools import tee

# Local
from crmprtd.wamr.download import download
from crmprtd.wamr.normalize import normalize
from crmprtd import setup_logging
from crmprtd import common_script_arguments


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--ftp_server',
                        default='ftp.env.gov.bc.ca',
                        help=('Full hostname of Water and Air Monitoring and '
                              'Reporting\'s ftp server'))
    parser.add_argument('-F', '--ftp_dir',
                        default=('pub/outgoing/AIR/Hourly_Raw_Air_Data/'
                                 'Meteorological/'),
                        help='FTP Directory containing WAMR\'s data files')

    parser = common_script_arguments(parser)
    args = parser.parse_args()
    log = setup_logging(args.log_conf, args.log,
                        args.error_email, args.log_level, 'crmprtd.wamr')

    download_iter = download(args)

    if args.cache_file:
        download_iter, cache_iter = tee(download_iter)
        with open(args.cache_file, 'w') as f:
            for chunk in cache_iter:
                f.write(chunk)

    for row in normalize(download_iter):
        print(row)
