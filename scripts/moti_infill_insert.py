#!/usr/bin/env python

import os
from optparse import OptionParser
from pkg_resources import resource_stream
import logging
import logging.config
from glob import glob

import yaml
from lxml.etree import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pycds import Station, History, Network, Variable
from pycds.util import create_test_database
from crmprtd.moti import process


def main(opts, args):
    log_conf = yaml.load(opts.log_conf)
    if opts.log:
        log_conf['handlers']['file']['filename'] = opts.log
    else:
        opts.log = log_conf['handlers']['file']['filename']
    if opts.error_email:
        log_conf['handlers']['mail']['toaddrs'] = opts.error_email
    logging.config.dictConfig(log_conf)
    # json logger
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    log.addHandler(logHandler)

    engine = create_engine(opts.connection_string)
    if opts.new_db:
        create_test_database(engine)

    if opts.source_dsn:
        copy_stations_to_sqlite(opts.source_dsn, opts.connection_string)

    sesh = sessionmaker(bind=engine)()

    files = glob(os.sep.join([opts.cache_dir, '*']))

    for file_ in files:
        print(file_)
        et = parse(file_)
        try:
            rv = process(sesh, et)
            logging.info("Processed file",
                         extra={'file': file_, 'results': rv})
        except Exception as e:
            logging.error(e)

# Just for testing inserts w/ sqlite


def copy_stations_to_sqlite(src_dsn, dest_dsn):
    src_sesh = sessionmaker(bind=create_engine(src_dsn))()
    dest_sesh = sessionmaker(bind=create_engine(dest_dsn))()

    net = Network(name='MoTIe')
    dest_sesh.add(net)
    dest_sesh.flush()

    q = src_sesh.query(Station).join(History).join(
        Network).filter(Network.name == 'MoTIe')
    for stn in q.all():
        histories = [History(station_name=hist.station_name)
                     for hist in stn.histories]
        new_obj = Station(native_id=stn.native_id,
                          network_id=net.id, histories=histories)
        dest_sesh.add(new_obj)
    dest_sesh.commit()

    q = src_sesh.query(Variable).join(Network).filter(Network.name == 'MoTIe')
    for var in q.all():
        v = Variable(name=var.name, standard_name=var.standard_name,
                     cell_method=var.cell_method, network_id=net.id,
                     unit=var.unit)
        dest_sesh.add(v)
    dest_sesh.commit()


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-c', '--connection_string',
                      dest='connection_string', help='SQLALchemy DSN')
    parser.add_option('-y', '--log_conf', dest='log_conf',
                      help=('YAML file to use to override the default logging '
                            'configuration'))
    parser.add_option('-l', '--log', dest='log', help="log filename")
    parser.add_option('-e', '--error_email', dest='error_email',
                      help=('e-mail address to which the program should '
                            'report error which require human intervention'))
    parser.add_option('-C', '--cache_dir', dest='cache_dir',
                      help=('directory from which to get the XML files to '
                            'process'))
    parser.add_option('-S', '--source_dsn', dest='source_dsn',
                      help=('optional DSN from which to get stations for '
                            'pre-insert'))
    parser.add_option('-n', '--new_db', dest='new_db',
                      help='create a fresh database at the connection_string?',
                      action="store_true")
    # parser.add_option('-o', '--output_dir', dest='output_dir',
    #                   help='directory in which to put the downloaded file')

    parser.set_defaults(connection_string='sqlite:////tmp/crmp.sqlite',
                        log_conf=resource_stream(
                            'crmprtd', '/data/logging.yaml'),
                        log=('/home/data/projects/crmp/data/MoTI_Downloads/'
                             'logs/'),
                        error_email='hiebert@uvic.ca',
                        cache_dir=('/home/data/projects/crmp/data/'
                                   'MoTI_Downloads/auto'),
                        source_dsn=None,
                        new_db=False,
                        )
    (opts, args) = parser.parse_args()
    main(opts, args)
