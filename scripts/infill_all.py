'''Infill crmprtd data for *all* networks for some time range
'''

import datetime
import logging
from argparse import ArgumentParser
from warnings import warn
from subprocess import run, PIPE
import itertools

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pycds import Station, Network
from dateutil.tz import tzlocal
import pytz

from crmprtd import logging_args, setup_logging


logger = logging.getLogger(__name__)


def main():
    desc = globals()['__doc__']
    parser = ArgumentParser(description=desc)
    parser.add_argument('-S', '--start_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')."))
    parser.add_argument('-E', '--end_time',
                        help=("Alternate time to use for downloading "
                              "(interpreted with "
                              "strptime(format='Y/m/d H:M:S')."))
    parser.add_argument('-a', '--auth_fname',
                        help="Yaml file with plaintext usernames/passwords")
    parser.add_argument('-c', '--connection_string',
                        help='PostgreSQL connection string',
                        required=True)

    parser = logging_args(parser)
    args = parser.parse_args()

    log_args = [args.log_conf, args.log_filename, args.error_email,
                args.log_level, 'infill_all']
    setup_logging(*log_args)

    fmt = '%Y/%m/%d %H:%M:%S'
    s = datetime.datetime.strptime(args.start_time, fmt).astimezone(tzlocal())
    e = datetime.datetime.strptime(args.end_time, fmt).astimezone(tzlocal())

    log_args = [(x, y) for (x, y) in zip(["-L", "-l", "-m", "-o"], log_args)
                if y]
    log_args = list(itertools.chain(*log_args))

    infill(s, e, args.auth_fname, args.connection_string, log_args)


def download_and_process(download_args, network_name, connection_string,
                         log_args):
    proc = [f"download_{network_name}"] + log_args + download_args
    logger.debug(' '.join(proc))
    dl_proc = run(proc, stdout=PIPE)
    process = ["crmprtd_process", "-c", connection_string,
               "-N", network_name] + log_args
    logger.debug(' '.join(process))
    run(process, input=dl_proc.stdout)


def infill(start_time, end_time, auth_fname, connection_string,
           log_args):

    weekly_ranges = list(
        datetime_range(start_time, end_time, resolution='week')
    )
    daily_ranges = list(datetime_range(start_time, end_time, resolution='day'))
    hourly_ranges = list(
        datetime_range(start_time, end_time, resolution='hour')
    )

    # Unfortunately most of the download functions only accepts a time
    # *string* :(
    time_fmt = '%Y/%m/%d %H:%M:%S'

    # EC
    for freq, times in zip(('daily', 'hourly'), (daily_ranges, hourly_ranges)):
        for province in ('YT', 'BC'):
            for time in times:
                time = time.astimezone(pytz.utc)  # EC files are named in UTC
                dl_args = ["-p", province, "-F", freq, "-g" "e",
                           "-t", time.strftime(time_fmt)]
                download_and_process(dl_args, "ec", connection_string,
                                     log_args)

    # MOTI
    # Query all of the stations
    stations = get_moti_stations(connection_string)
    # Divide range into 7 day intervals
    for interval_start, interval_end in zip(
            weekly_ranges[:-1], weekly_ranges[1:]):
        for station in stations:
            start = interval_start.strftime(time_fmt)
            end = interval_end.strftime(time_fmt)
            dl_args = ["--auth_fname", auth_fname,
                       "--auth_key", "moti", "-S", start, "-E", end,
                       "-s", station]
            download_and_process(dl_args, "moti", connection_string, log_args)

    warning_msg = {
        "disjoint":
            "{} cannot be infilled since the period of infilling is "
            "outside the currently offered data (the previous {}).",
        "not_contained":
            "{} infilling may miss some data since the requested infilling"
            " period is larger than the currently offered period of record "
            "(the previous {})."
    }
    now = datetime.datetime.now()

    # WAMR
    # Check that the interval overlaps with the last month
    last_month = (now - datetime.timedelta(days=30), now)
    # Warn if not
    if not interval_overlaps((start_time, end_time), last_month):
        warn(warning_msg['disjoin'].format("WAMR", "one month"))
    else:
        if not interval_contains((start_time, end_time), last_month):
            warn(warning_msg['not_contained'].format("WAMR", "one_month"))
        dl_args = []
        download_and_process(dl_args, 'wamr', connection_string, log_args)

    # WMB
    yesterday = (now - datetime.timedelta(days=1), now)
    # Check that the interval overlaps with the last day
    # Warn if not
    if not interval_overlaps((start_time, end_time), yesterday):
        warn(warning_msg['disjoint'].format("WMB", "day"))
    else:
        if not interval_contains((start_time, end_time), yesterday):
            warn(warning_msg['not_contained'].format("WMB", "day"))
        # Run it
        dl_args = ["--auth_fname", auth_fname, "--auth_key", "wmb"]
        download_and_process(dl_args, 'wmb', connection_string, log_args)

    # EC_SWOB
    for partner in ('bc_env_snow', 'bc_tran', 'bc_forestry'):
        for hour in hourly_ranges:
            hour = hour.astimezone(pytz.utc)  # EC files are named in UTC
            dl_args = ["-d", hour.strftime(time_fmt)]
            download_and_process(dl_args, partner, connection_string, log_args)


def round_datetime(d, resolution='hour', direction='down'):
    d = d.replace(minute=0, second=0, microsecond=0)
    if resolution == 'day':
        d = d.replace(hour=0)
    elif resolution == 'hour':
        pass
    else:
        raise ValueError(f"resolution parameter can only be 'hour' or 'day' "
                         "not '{resolution}'")
    if direction == 'up':
        kwargs = {resolution + 's': 1}
        delta = datetime.timedelta(**kwargs)
    elif direction == 'down':
        delta = datetime.timedelta()
    else:
        raise ValueError(f"direction parameter can only be 'down' or 'up' "
                         "not '{direction}'")

    return d + delta


def datetime_range(start, end, resolution='hour'):
    if resolution not in ('hour', 'day', 'week'):
        raise ValueError
    kwargs = {resolution + 's': 1}
    step = datetime.timedelta(**kwargs)

    # Don't round down to the week... just the day and end at the actual end
    if resolution == 'week':
        start = round_datetime(start, 'day', direction='down')
        # Otherwise, make a rounded timeseries to the day or hour
    else:
        start = round_datetime(start, resolution, direction='down')
        end = round_datetime(end, resolution, direction='up')

    t = start
    while t < end:
        yield t
        t += step
    yield end


def interval_contains(a, b):
    '''time interval a contains time interval b'''
    return a[0] <= b[0] and a[1] >= b[1]


def interval_overlaps(a, b):
    '''time interval a and b contain some overlap'''
    return max(a[0], b[0]) <= min(a[1], b[1])


def get_moti_stations(connection_string):
    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    q = sesh.query(Station.native_id).join(Network)\
                                     .filter(Network.name == "MoTIe")
    return [native_id for (native_id,) in q.all()]


if __name__ == '__main__':
    main()
