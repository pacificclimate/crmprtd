#!/usr/bin/env python

# Standard module
from argparse import ArgumentParser

# Local
from crmprtd.moti.download import download
from crmprtd.moti.normalize import normalize
from crmprtd import common_script_arguments, setup_logging, run_data_pipeline,\
    subset_dict


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
    parser.add_argument('--auth',
                        help="Yaml file with plaintext usernames/passwords")
    parser.add_argument('--auth_key',
                        help=("Top level key which user/pass are stored in "
                              "yaml file."))
    parser.add_argument('--bciduser',
                        help=("The BCID username for data requests. Overrides "
                              "auth file."))
    parser.add_argument('--bcidpass',
                        help=("The BCID password for data requests. Overrides "
                              "auth file."))
    parser = common_script_arguments(parser)
    args = parser.parse_args()
    log = setup_logging(args.log_conf, args.log,
                        args.error_email, args.log_level, 'crmprtd.moti')

    dl_args = ['start_time', 'end_time', 'station_id', 'auth',
               'auth_key', 'bciduser', 'bcidpass']
    dl_args = subset_dict(vars(args), dl_args)

    run_data_pipeline(download, normalize, dl_args, args.cache_file)
