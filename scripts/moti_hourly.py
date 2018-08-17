#!/usr/bin/env python

# Standard module
from argparse import ArgumentParser

# Local
from crmprtd.moti.download import download
from crmprtd.moti.normalize import normalize
from crmprtd import common_script_arguments, common_auth_arguments, \
    setup_logging, run_data_pipeline, subset_dict


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-S', '--start_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')"))
    parser.add_argument('-E', '--end_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')"))
    parser.add_argument('-s', '--station_id',
                        help="Station ID for which to download data")
    parser = common_script_arguments(parser)
    parser = common_auth_arguments(parser)
    args = parser.parse_args()
    setup_logging(args.log_conf, args.log, args.error_email, args.log_level,
                  'crmprtd.moti')

    dl_args = ['start_time', 'end_time', 'station_id', 'auth_fname',
               'auth_key', 'username', 'password']
    dl_args = subset_dict(vars(args), dl_args)

    run_data_pipeline(download, normalize, dl_args, args.cache_file,
                      args.connection_string, args.sample_size)
