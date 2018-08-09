#!/usr/bin/env python

# Standard module
import os
import sys
from datetime import datetime, timedelta
from argparse import ArgumentParser
import logging

# Installed libraries
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from crmprtd import setup_logging, common_script_arguments, \
    common_auth_arguments
from crmprtd.ec import makeurl, ObsProcessor, parse_xml, extract_fname_from_url


def main(args):
    log = logging.getLogger('crmprtd.ec')
    log.info('Starting EC rtd')

    try:
        if args.input_file:
            log.debug("Opening local xml filefor reading",
                      extra={'file': args.input_file})
            fname = args.input_file
            log.debug("File opened sucessfully")
        else:

            # Determine time parameter
            if args.time:
                args.time = datetime.strptime(args.time, '%Y/%m/%d %H:%M:%S')
                log.info("Starting manual run using timestamp",
                         extra={'timestamp': args.time})
            else:
                # go back a day
                deltat = timedelta(
                    1 / 24.) if args.frequency == 'hourly' else timedelta(1)
                args.time = datetime.utcnow() - deltat
                log.info("Starting automatic run using timestamp",
                         extra={'timestamp': args.time})

            # Configure requests to use retry
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('https://', a)

            # Construct and download the xml
            url = makeurl(args.frequency, args.province,
                          args.language, args.time)
            fname = os.path.join(args.cache_dir, extract_fname_from_url(url))

            log.info("Downloading", extra={'url': url})
            req = s.get(url)
            if req.status_code != 200:
                raise IOError("HTTP {} error for {}".format(
                    req.status_code, req.url))

            log.info("Saving data file", extra={'fname': fname})
            with open(fname, 'wb') as f:
                f.write(req.content)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)

    # Wrap critical secion
    try:
        log.info("Parsing input xml")
        et = parse_xml(fname)

        log.info("Creating database session")
        Session = sessionmaker(create_engine(args.connection_string))
        sesh = Session()

    except Exception as e:
        log.critical('Critical errors have occured in the EC real time '
                     'downloader', extra={'log_file': args.log_filename,
                                          'data_archive': fname})
        sys.exit(1)

    try:
        # BEGIN NESTED #
        sesh.begin_nested()
        log.info("Starting observation processing")
        op = ObsProcessor(et, sesh, args.threshold)
        op.process()
        log.info("Done processing observations")
        if args.diag:
            log.info('Diagnostic mode, rolling back all transactions')
            sesh.rollback()
        else:
            log.info('Commiting the session')
            sesh.commit()
        # END BEGIN NESTED #

    except Exception as e:
        sesh.rollback()
        log.critical('Critical errors have occured in the EC real time '
                     'downloader', extra={'log_file': args.log_filename,
                                          'data_archive': fname})
        sys.exit(1)

    finally:
        sesh.commit()
        sesh.close()


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
    setup_logging(args.log_conf, args.log_filename, args.error_email,
                        args.log_level, 'crmprtd.ec')
    main(args)
