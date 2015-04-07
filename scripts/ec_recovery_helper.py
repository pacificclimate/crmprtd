#!/usr/bin/env python

# Very basic recovery string generation script terribly implemented
# Not intended as anything more than a convenience function when performing a manual recovery on EC data

# Standard module
import os, sys
from datetime import datetime, timedelta
from optparse import OptionParser
from pkg_resources import resource_stream

# Local
from real_time_ec import main as ec_recover

# debug
from pdb import set_trace

def makeDir(d):
    if not os.path.exists(d):
        os.makedirs(d)
    return d

def main(opts, args):
    # It is assumed that start and end times are correctly formatted on entry
    # Exceptions are not handled by design.
    stime = datetime.strptime(opts.stime, '%Y/%m/%d %H:%M:%S')
    etime = datetime.strptime(opts.etime, '%Y/%m/%d %H:%M:%S')

    ss = stime.strftime('%Y%m%d%H')
    ee = etime.strftime('%Y%m%d%H')
    
    logdir = makeDir(os.path.join(opts.logdir, 'EC_' + stime.strftime('%Y%m%d') + '_' + opts.reason))

    script = os.path.join(opts.prefix, 'ec_recovery.py')

    with open(os.path.join(logdir, 'recovery.txt'), 'w') as f:
        for prov in ['BC', 'YT']:
            for freq in ['hourly', 'daily']:
                s = "python {script} -e bveerman@uvic.ca -c '{conn_string}' -p {prov} -F {freq} --starttime '{s}' --endtime '{e}' --threshold 1000 -l {logdir}/ec_recovery_{prov}_{freq}_{ss}_{ee}.log".format(script=script, conn_string=opts.conn_string, prov=prov, freq=freq, s=opts.stime, e=opts.etime, logdir=logdir, ss=ss, ee=ee)
                f.write(s)
                print s
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c', '--conn_string', dest='conn_string', help='PostgreSQL connection string')
    parser.add_option('-e', '--error_email', dest='error_email', help='e-mail address to which the program should report error which require human intervention')
    parser.add_option('--logdir', help='Base directory in which to create a date specific dir for log files.  Must have write permissions')
    parser.add_option('--reason', help='Tag the folder created with a reason for the recovery')
    parser.add_option('--prefix', help='Script location prefix if recovery script not in PATH')
    parser.add_option('--starttime', dest='stime', help="Start time of range to recover (interpreted with strptime(format='%Y/%m/%d %H:%M:%S')")
    parser.add_option('--endtime', dest='etime', help="End time of range to recover (interpreted with strptime(format='%Y/%m/%d %H:%M:%S')")
    parser.add_option('-T', '--threshold', dest='thresh', help='Distance threshold to use when matching stations.  Stations are considered a match if they have the same id, name, and are within this threshold')
    parser.add_option('-D', '--diag', dest='diag', action="store_true", help="Turn on diagnostic mode (no commits)")

    parser.set_defaults(conn_string='dbname=crmp user=crmprtd',
                        error_email='bveerman@uvic.ca',
                        logdir='/home/data/projects/crmp/recovery',
                        reason=None,
                        prefix='',
                        stime=None,
                        etime=None,
                        diag=False,
                        thresh=0
                        )
    (opts, args) = parser.parse_args()
    main(opts, args)
