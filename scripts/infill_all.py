'''Infill crmprtd data for *all* networks for some time range
'''

import datetime
from argparse import ArgumentParser
from warnings import warn

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pycds import Station, Network

from crmprtd import logging_args, setup_logging
from crmprtd.ec.download import download as ec_download
from crmprtd.moti.download import download as moti_download
from crmprtd.wmb.download import download as wmb_download
from crmprtd.wamr.download import download as wamr_download
from crmprtd.ec_swob.download import download as swob_download


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

    setup_logging(args.log_conf, args.log_filename, args.error_email,
                  args.log_level, 'infill_all')
    s = datetime.datetime.strptime(args.start_time, '%Y/%m/%d %H:%M:%S')
    e = datetime.datetime.strptime(args.end_time, '%Y/%m/%d %H:%M:%S')
    infill(s, e, args.auth_fname)


def infill(start_time, end_time, auth_fname, connection_string):

    weekly_ranges = list(datetime_range(start_time, end_time, resolution='week'))
    daily_ranges = list(datetime_range(start_time, end_time, resolution='day'))
    hourly_ranges = list(datetime_range(start_time, end_time, resolution='hour'))

    # Unfortunately most of the download functions only accepts a time
    # *string* :(
    time_fmt = '%Y/%m/%d %H:%M:%S'

    process = ["crmprtd_process", f"-c {connection_string}"]
    
    # EC
    for freq, times in zip(('daily', 'hourly'), (daily_ranges, hourly_ranges)):
        for province in ('YT', 'BC'):
            for time in times:
                proc = ["download_ec", f"-p {province}", f"-F {freq}", "-g e",
                        f"-t {time.strftime(time_fmt)}"]
                print(proc.join(' '))
                dl_proc = run(proc, capture_output=True)
                process_proc = run(process + ["-N ec"], stdin=dl_proc.stdout)

    # MOTI
    # Query all of the stations
    stations = get_moti_stations(connection_string)
    # Divide range into 7 day intervals
    for interval_start, interval_end in zip(
            weekly_ranges[:-1], weekly_ranges[1:]):
        for station in stations:
            start = interval_start.strftime(time_fmt)
            end = interval_end.strftime(time_fmt)
            print(f"moti_download('', '', {auth_fname}, 'moti',"
                          f"{start}, {end}, {station})")

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
        print("wamr_download('ftp.env.gov.bc.ca', 'pub/outgoing/AIR/'"
                      "'Hourly_Raw_Air_Data/Meteorological/')")
        
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
        print(f"wmb_download("
            f"'', '', {auth_fname}, 'wmb',"
            f"'BCFireweatherFTPp1.nrs.gov.bc.ca',"
            f"'HourlyWeatherAllFields_WA.txt'"
              f")")

    # EC_SWOB
    for partner in ('bc_env_snow', 'bc_tran', 'bc_forestry'):
        print(partner)
        for hour in hourly_ranges:
            print(hour)
            print(f"swob_download("
                f"f'https://dd.weather.gc.ca/observations/swob-ml/partners/{partner}/',"
                f"{hour.strftime(time_fmt)}"
                  f")")


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

    i = 0
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
