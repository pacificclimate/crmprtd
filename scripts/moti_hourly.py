#!/usr/bin/env python

# Standard module
from argparse import ArgumentParser
from pkg_resources import resource_stream
from itertools import tee

# Local
from crmprtd.moti.download import download
from crmprtd.moti.normalize import normalize
from crmprtd.moti import logging_setup
from crmprtd import iterable_to_stream, common_script_arguments


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
    log = logging_setup(args.log_conf, args.log,
                        args.error_email, args.log_level)

    download_iter = download(args)

    if args.cache_file:
        download_iter, cache_iter = tee(download_iter)
        with open(args.cache_file, 'wb') as f:
            stream = iterable_to_stream(cache_iter)
            f.write(stream.read())

    stream = iterable_to_stream(download_iter)
    for line in normalize(stream):
        print(line)
