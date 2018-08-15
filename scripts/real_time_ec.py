#!/usr/bin/env python

# Standard module
from argparse import ArgumentParser

# Local
from crmprtd.ec.download import download
from crmprtd.ec.normalize import normalize
from crmprtd import common_script_arguments, setup_logging, run_data_pipeline,\
    subset_dict


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--province', required=True,
                        help='2 letter province code')
    parser.add_argument('-g', '--language', default='e',
                        choices=['e', 'f'],
                        help="'e' (english) | 'f' (french)")
    parser.add_argument('-F', '--frequency', required=True,
                        choices=['daily', 'hourly'],
                        help='daily|hourly')
    parser.add_argument('-t', '--time',
                        help=("Alternate *UTC* time to use for downloading "
                              "(interpreted using "
                              "format=YYYY/MM/DD HH:MM:SS)"))
    parser.add_argument('-T', '--threshold', default=1000,
                        help=('Distance threshold to use when matching '
                              'stations.  Stations are considered a match if '
                              'they have the same id, name, and are within '
                              'this threshold'))
    parser = common_script_arguments(parser)
    args = parser.parse_args()
    log = setup_logging(args.log_conf, args.log,
                        args.error_email, args.log_level, 'crmprtd.ec')

    dl_args = ['time', 'frequency', 'province', 'language']
    dl_args = subset_dict(vars(args), dl_args)

    run_data_pipeline(download, normalize, dl_args, args.cache_file,
                      args.connection_string, args.sample_size)
