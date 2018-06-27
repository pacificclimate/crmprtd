#!/usr/bin/env python

# Standard module
import os
import glob
import logging
import logging.config
from argparse import ArgumentParser
from pkg_resources import resource_stream
from shutil import move

# Installed libraries
from lxml.etree import parse
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd.moti import process


def main(args):
    # Setup logging
    log_conf = yaml.load(args.log_conf)
    if args.log:
        log_conf['handlers']['file']['filename'] = args.log
    else:
        args.log = log_conf['handlers']['file']['filename']
    if args.error_email:
        log_conf['handlers']['mail']['toaddrs'] = args.error_email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger('crmprtd.moti')
    if args.log_level:
        log.setLevel(args.log_level)
    # json logger
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    log.addHandler(logHandler)
    log.info('Starting MOTIe rtd')

    # Generate file list if necessary
    if args.file_pattern:
        log.info('Using file pattern',
                 extra={'file_pattern': args.file_patter})
        f_list = glob.glob(args.file_pattern)
    elif args.filename:
        f_list = [args.filename]

    log.info('Processing files', extra={'num_files': len(f_list)})

    for fname in f_list:
        log.info('Processing file', extra={'file': fname})

        Session = sessionmaker(create_engine(args.connection_string))
        sesh = Session()
        sesh.begin_nested()
        try:
            with open(fname, 'r') as xml_file:
                et = parse(xml_file)
            r = process(sesh, et)
            log.info(r)
            if args.diag:
                log.info('Diagnostic mode, rolling back')
                sesh.rollback()
            else:
                log.info('Comitting session')
                sesh.commit()
        except Exception as e:
            sesh.rollback()
            log.critical('Serious errors with MOTIe rtd, see logs', extra={'log': args.log})
            continue
        else:
            move(fname, os.path.join(args.output_dir, os.path.basename(fname)))
        finally:
            sesh.commit()
            sesh.close()


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
                        default=resource_stream(
                            'crmprtd', '/data/logging.yaml'),
                        help=('YAML file to use to override the default '
                              'logging configuration'))
    parser.add_argument('-l', '--log', help="log filename")
    parser.add_argument('-e', '--error_email',
                        help=('e-mail address to which the program should '
                              'report error which require human intervention'))
    parser.add_argument('--log_level',
                        choices=['DEBUG', 'INFO',
                                 'WARNING', 'ERROR', 'CRITICAL'],
                        help=('Set log level: DEBUG, INFO, WARNING, ERROR, '
                              'CRITICAL.  Note that debug output by default '
                              'goes directly to file'))
    parser.add_argument('-p', '--file_pattern', default=None,
                        help='directory to process for xml files')
    parser.add_argument('-f', '--filename', default=None,
                        help='MPO-XML file to process')
    parser.add_argument('-o', '--output_dir', required=True,
                        help='directory to move successfully imported files')

    parser.add_argument('-D', '--diag', action="store_true", default=False,
                        help="Turn on diagnostic mode (no commits)")

    args = parser.parse_args()
    main(args)
