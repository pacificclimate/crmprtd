#!/usr/bin/env python

# Standard module
import os
import sys
import logging
import logging.config
from datetime import datetime, timedelta
from argparse import ArgumentParser
from pkg_resources import resource_filename

# Installed libraries
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml

# Local
from crmprtd.ec import makeurl, ObsProcessor, parse_xml, extract_fname_from_url
from crmprtd.ec.download import run



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--connection_string', required=True,
                        help=('PostgreSQL connection string of form:'
                              '\n\tdialect+driver://username:password@host:'
                              'port/database\n'
                              'Examples:'
                              '\n\tpostgresql://scott:tiger@localhost/'
                              'mydatabase'
                              '\n\tpostgresql+psycopg2://scott:tiger@'
                              'localhost/mydatabase'
                              '\n\tpostgresql+pg8000://scott:tiger@localhost'
                              '/mydatabase'))
    parser.add_argument('-y', '--log_conf',
                        default=resource_filename(
                            'crmprtd', '/data/logging.yaml'),
                        help=('YAML file to use to override the default '
                              'logging configuration'))
    parser.add_argument('-l', '--log',
                        help="log filename")
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        help=('Set log level: DEBUG, INFO, WARNING, ERROR, '
                              'CRITICAL.  Note that debug output by default '
                              'goes directly to file'))
    parser.add_argument('-e', '--error_email',
                        help=('e-mail address to which the program should '
                              'report error which require human intervention'))
    parser.add_argument('-C', '--cache_dir', required=True,
                        help=('directory in which to put the downloaded file '
                              'in the event of a post-download error'))
    parser.add_argument('-f', '--filename',
                        help='MPO-XML file to process')
    parser.add_argument('-p', '--province', required=True,
                        help='2 letter province code')
    parser.add_argument('-L', '--language', default='e',
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
    parser.add_argument('-D', '--diag', default=False, action="store_true",
                        help="Turn on diagnostic mode (no commits)")

    args = parser.parse_args()
    run(args)
