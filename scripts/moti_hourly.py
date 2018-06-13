#!/usr/bin/env python

# Standard module
import os, sys
import logging, logging.config
from datetime import datetime, timedelta
from argparse import ArgumentParser
import requests
from traceback import print_exc
from pkg_resources import resource_stream

# Installed libraries
from lxml.etree import LxmlSyntaxError
from lxml.etree import parse
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd import retry
from crmprtd.moti import makeurl, process
from crmprtd.moti.download import run

# debug
from pdb import set_trace


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string of form:\n\tdialect+driver://username:password@host:port/database\nExamples:\n\tpostgresql://scott:tiger@localhost/mydatabase\n\tpostgresql+psycopg2://scott:tiger@localhost/mydatabase\n\tpostgresql+pg8000://scott:tiger@localhost/mydatabase')
    parser.add_argument('-y', '--log_conf',
                        default = resource_stream('crmprtd', '/data/logging.yaml'),
                        help='YAML file to use to override the default logging configuration')
    parser.add_argument('-l', '--log', help="log filename")
    parser.add_argument('-e', '--error_email',
                        help='e-mail address to which the program should report error which require human intervention')
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.  Note that debug output by default goes directly to file')
    parser.add_argument('-C', '--cache_dir', required = True,
                        help='directory in which to put the downloaded file in the event of a post-download error')
    parser.add_argument('-f', '--filename',
                        help='MPO-XML file to process')
    parser.add_argument('-S', '--start_time',
                        help="Alternate time to use for downloading (interpreted with strptime(format='Y/m/d H:M:S')")
    parser.add_argument('-E', '--end_time',
                        help="Alternate time to use for downloading (interpreted with strptime(format='Y/m/d H:M:S')")
    parser.add_argument('-i', '--station_id',
                        help="Station ID for which to download data")
    parser.add_argument('--auth', help="Yaml file with plaintext usernames/passwords")
    parser.add_argument('--auth_key', help="Top level key which user/pass are stored in yaml file.")
    parser.add_argument('--bciduser', help="The BCID username for data requests. Overrides auth file.")
    parser.add_argument('--bcidpass', help="The BCID password for data requests. Overrides auth file.")
    parser.add_argument('-D', '--diag', action="store_true", default = False,
                        help="Turn on diagnostic mode (no commits)")
    # parser.add_argument('-o', '--output_dir', dest='output_dir', help='directory in which to put the downloaded file')

    args = parser.parse_args()
    run(args)
