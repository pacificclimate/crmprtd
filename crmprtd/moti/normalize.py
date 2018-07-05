#!/usr/bin/env python

# Standard module
import sys

# Installed libraries
from lxml.etree import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pkg_resources import resource_filename
from lxml.etree import parse, XSLT

# Local
from crmprtd.moti import process
from crmprtd import Row


def prepare(args, log, infile):
    Session = sessionmaker(create_engine(args.connection_string))
    sesh = Session()
    sesh.begin_nested()
    try:
        et = parse(infile)
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
        log.critical('Serious errros with MOTIe rtd, see logs',
                     extra={'log': args.log})
        sys.exit(1)
    finally:
        sesh.commit()
        sesh.close()

xsl = resource_filename('crmprtd', 'data/moti.xsl')
transform = XSLT(parse(xsl))


def normalize(file_stream):
    et = parse(file_stream)
    et = transform(et)
    print(et)
    obs_series = et.xpath("//observation-series")
    # for series in obs_series:
    #     print('we get here')
    #     try:
    #         stn_id = os.xpath("./origin/id[@type='client']")[0].text.strip()
    #     except IndexError as e:
    #         raise Exception(
    #             "Could not detect the station id: xpath search "
    #             "'//observation-series/origin/id[@type='client']' return no "
    #             "results")
    #     print(stn_id)
