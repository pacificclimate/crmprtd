#!/usr/bin/env python

# Standard module
import os, sys
import logging, logging.config
from datetime import datetime, timedelta
from optparse import OptionParser
from urllib import urlopen
from traceback import print_exc
from pkg_resources import resource_stream

# Installed libraries
from psycopg2 import InterfaceError, ProgrammingError, OperationalError
from lxml.etree import LxmlSyntaxError
import yaml

# Local
from crmprtd.ec import makeurl, ObsProcessor

# debug
from pdb import set_trace

def main(opts, args):
    # Setup logging
    log_conf = yaml.load(opts.log_conf)
    if opts.log:         log_conf['handlers']['file']['filename'] = opts.log
    else:                opts.log = log_conf['handlers']['file']['filename']
    if opts.error_email: log_conf['handlers']['mail']['toaddrs'] = opts.error_email
    logging.config.dictConfig(log_conf)

    auto = True
    try:
        if opts.filename:
            logging.debug("Opening local xml file {0} for reading".format(opts.filename))
            auto = False
            fname = opts.filename
            xml_file = open(opts.filename, 'r')
            logging.debug("File opened sucessfully")
        else:
            if opts.time:
                opts.time = datetime.strptime(opts.time, '%Y/%m/%d %H:%M:%S')
                logging.info("Starting manual run using timestamp {0}".format(opts.time))
                auto = False
            else:
                deltat = timedelta(1/24.) if opts.frequency == 'hourly' else timedelta(1) # go back a day
                opts.time = datetime.utcnow() - deltat
                logging.info("Starting automatic run using timestamp {0}".format(opts.time))
            url = makeurl(opts.frequency, opts.province, opts.language, opts.time)
            fname = url['filename']
            logging.info("Downloading {0}".format(url['url']))
            xml_file = urlopen(url['url'])
            if xml_file.getcode() == 404: raise IOError("HTTP 404 error for %s" % url['url'])
    except IOError:
        logging.exception("Unable to download or open xml data")
        sys.exit(1)

    # instantiate the ObsProcessor (do the startup stuff, like opening db connection and parsing the XML)
    try:
        logging.info("Instantiating the ObsProcessor",)
        op = ObsProcessor(xml_file, opts)
        logging.info("Done setting up ObsProcessor")
    except (LxmlSyntaxError, IOError, OperationalError), e:
        if type(e) == OperationalError:
            logging.exception("Could not connect to database")
        if type(e) == LxmlSyntaxError:
            logging.exception("Failed to parse xml file \n {0}".format(xml_file))
        if type(e) == IOError:
            logging.exception("Failed to open xml file\n{0}".format(xml_file))
        # Save data for reprosessing
        if auto:
            fname = os.path.join(opts.cache_dir, 'failure-' + fname)
        else:
            fname = os.path.join(opts.cache_dir, 'manual_run_' + datetime.now().strftime('%Y%m%dT%H%M%S') + '_failure-' + fname)
        logging.info("Saving data at: {}".format(fname))
        f = open(fname, 'w')
        f.write(xml_file.read())
        logging.info("Done saving data")
        logging.critical('''Critical errors have occured in the EC real time downloader that require a human touch.
        The daemon was unable to either download, open, or parse the incoming xml and no observations could be inserted.
        Please consult the log file at {log}.
        Data has been archived at {f}.'''.format(log=opts.log, f=fname))
        sys.exit(1)

    # process the XML and do the db insertions
    try:
        logging.info("Starting to process observations")
        op.process()
        logging.info("Done processing observations")
    except (InterfaceError, ProgrammingError, Exception), e:
        logging.exception("Unhandleable exception, saving remaining XML file {} for further examination".format(fname))
    finally:
        if auto:
            remainder = os.path.join(opts.cache_dir, 'remainder-' + fname)
        else:
            remainder = os.path.join(opts.cache_dir, 'manual_run_' + datetime.now().strftime('%Y%m%dT%H%M%S') + '_remainder-' + fname)
        op.save(remainder)
        logging.info("Data saved at {}".format(remainder))

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-c', '--connection_string', dest='connection_string', help='PostgreSQL connection string of form:\n\tdialect+driver://username:password@host:port/database\nExamples:\n\tpostgresql://scott:tiger@localhost/mydatabase\n\tpostgresql+psycopg2://scott:tiger@localhost/mydatabase\n\tpostgresql+pg8000://scott:tiger@localhost/mydatabase')
    parser.add_option('-y', '--log_conf', dest='log_conf', help='YAML file to use to override the default logging configuration')
    parser.add_option('-l', '--log', dest='log', help="log filename")
    parser.add_option('-e', '--error_email', dest='error_email', help='e-mail address to which the program should report error which require human intervention')
    parser.add_option('-C', '--cache_dir', dest='cache_dir', help='directory in which to put the downloaded file in the event of a post-download error')
    parser.add_option('-f', '--filename', dest='filename', help='MPO-XML file to process')
    parser.add_option('-p', '--province', dest='province', help='2 letter province code')
    parser.add_option('-L', '--language', dest='language', help="'e' (english) | 'f' (french)")
    parser.add_option('-F', '--frequency', dest='frequency', help='daily|hourly')
    parser.add_option('-t', '--time', dest='time', help="Alternate time to use for downloading (interpreted with strptime(format='%Y/%m/%d %H:%M:%S')")
    parser.add_option('-T', '--threshold', dest='thresh', help='Distance threshold to use when matching stations.  Stations are considered a match if they have the same id, name, and are within this threshold')
    parser.add_option('-D', '--diag', dest='diag', action="store_true", help="Turn on diagnostic mode (no commits)")
    # parser.add_option('-o', '--output_dir', dest='output_dir', help='directory in which to put the downloaded file')

    parser.set_defaults(connection_string='dbname=rtcrmp user=crmp',
                        log_conf = resource_stream('crmprtd', '/data/logging.yaml'),
                        log=None,
                        error_email='hiebert@uvic.ca',
                        cache_dir='/home/data/projects/crmp/data/EC_Downloads/auto',
                        #filename='/tmp/hourly_bc_2011111416_e.xml',
                        filename=None,
                        province='BC', language='e', frequency='daily',
                        time=None,
                        diag=False,
                        thresh=0
                        )
    (opts, args) = parser.parse_args()
    main(opts, args)
