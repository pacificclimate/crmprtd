#!/usr/bin/env python

# Standard module
import os, sys
from datetime import datetime, timedelta
from optparse import OptionParser
from pkg_resources import resource_stream

# Local
from real_time_ec import main as ec_recover

# debug
from pdb import set_trace

def main(opts, args):
    # It is assumed that start and end times are correctly formatted on entry
    # Exceptions are not handled by design.
    stime = datetime.strptime(opts.stime, '%Y/%m/%d %H:%M:%S')
    etime = datetime.strptime(opts.etime, '%Y/%m/%d %H:%M:%S')
    if opts.filename or opts.time:
        raise Exception("Incorrect invocation, this wrapper only works on startime-endtime ranges to download data")
    assert stime < etime, "Start time must be less than end time... otherwise why are you using this?"

    if opts.frequency == 'hourly':
        timestep = timedelta(hours=1)
    elif opts.frequency == 'daily':
        timestep = timedelta(days=1)

    while stime <= etime:
        opts.time = datetime.strftime(stime, '%Y/%m/%d %H:%M:%S')
        ec_recover(opts, args)
        stime += timestep
        opts.log_conf.seek(0) #need to reset the resource stream back to 0
    
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-c', '--connection_string', dest='connection_string', help='PostgreSQL connection string')
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
    parser.add_option('--starttime', dest='stime', help="Start time of range to recover (interpreted with strptime(format='%Y/%m/%d %H:%M:%S')")
    parser.add_option('--endtime', dest='etime', help="End time of range to recover (interpreted with strptime(format='%Y/%m/%d %H:%M:%S')")

    parser.set_defaults(connection_string='dbname=rtcrmp user=crmp',
                        log_conf = resource_stream('crmprtd', '/data/logging.yaml'),
                        log='/tmp/crmp/ec_recovery.txt',
                        error_email='bveerman@uvic.ca',
                        cache_dir='/home/data/projects/crmp/rtd/EC',
                        filename = None,
                        province='BC', language='e', frequency='daily',
                        time=None,
                        stime=None,
                        etime=None,
                        diag=False,
                        thresh=0
                        )
    (opts, args) = parser.parse_args()
    main(opts, args)
