#!/usr/bin/env python

'''
Script to download data from the BC Ministry of Environment Air Quality Branch

Water and Air Monitoring and Reporting? (WAMR)

This is largely lifted and modified from the hourly_wmb.py script
'''


from argparse import ArgumentParser

# Local
from crmprtd.wamr.download import download
from crmprtd.wamr.normalize import normalize
from crmprtd import common_script_arguments, setup_logging, run_data_pipeline,\
    subset_dict


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

    dl_args = ['ftp_server', 'ftp_dir']
    dl_args = subset_dict(vars(args), dl_args)

    run_data_pipeline(download, normalize, dl_args, args.cache_file,
                      args.connection_string)
