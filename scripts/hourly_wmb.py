#!/usr/bin/env python

# From Jim Colley <Jim.Colley@gov.bc.ca>
# "The first file contains a rolling 24hrs of data for each station, and is
# updated at approximately 00:35 past each hour"
#
# FIXME: Replace opts.log with native python logging configuration
# FIMXE: Replace email_error with using a logging handler to catch critical
# errors (i.e. logger.critical()) and do the email

from argparse import ArgumentParser

# Local
from crmprtd.wmb.download import download
from crmprtd.wmb.normalize import normalize
from crmprtd import common_script_arguments, common_auth_arguments, \
    setup_logging, run_data_pipeline, subset_dict


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
    parser = common_script_arguments(parser)
    parser = common_auth_arguments(parser)
    args = parser.parse_args()
    setup_logging(args.log_conf, args.log_filename,
                  args.error_email, args.log_level, 'crmprtd.wmb')

    dl_args = ['username', 'password', 'auth_fname', 'auth_key', 'ftp_server',
               'ftp_file']
    dl_args = subset_dict(vars(args), dl_args)

    run_data_pipeline(download, normalize, dl_args, args.cache_file,
                      args.connection_string, args.sample_size)
