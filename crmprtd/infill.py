import re
import logging
import datetime
from warnings import warn
from subprocess import run, PIPE
import itertools

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pycds import Station, Network
from dateutil.tz import tzlocal
import pytz


logger = logging.getLogger(__name__)


def download_and_process(download_args, network_name, connection_string, log_args):
    """Open two subprocesses: download_{network} and crmprtd_process and
    pipe the output from the first to the second. Returns None.
    """
    proc = [f"download_{network_name}"] + log_args + download_args
    logger.debug(" ".join(proc))
    dl_proc = run(proc, stdout=PIPE)
    process = [
        "crmprtd_process",
        "-c",
        connection_string,
        "-N",
        network_name,
    ] + log_args
    message = " ".join(process)
    message = re.sub(r'postgresql:\/\/(.*?)\@', r'postgresql://', message)
    logger.debug(message)
    run(process, input=dl_proc.stdout)


def infill(networks, start_time, end_time, auth_fname, connection_string, log_args):
    """Setup and delegate all of the infilling processes"""
    monthly_ranges = list(datetime_range(start_time, end_time, resolution="month"))
    weekly_ranges = list(datetime_range(start_time, end_time, resolution="week"))
    daily_ranges = list(datetime_range(start_time, end_time, resolution="day"))
    hourly_ranges = list(datetime_range(start_time, end_time, resolution="hour"))

    # Unfortunately most of the download functions only accepts a time
    # *string* :(
    time_fmt = "%Y/%m/%d %H:%M:%S"

    # CRD
    if "crd" in networks:
        # Divide range into 28 day intervals
        for interval_start, interval_end in zip(
            monthly_ranges[:-1], monthly_ranges[1:]
        ):
            start = interval_start.strftime(time_fmt)
            end = interval_end.strftime(time_fmt)
            dl_args = [
                "-S",
                start,
                "-E",
                end,
                "--auth_fname",
                auth_fname,
                "--auth_key",
                "crd",
            ]
            download_and_process(dl_args, "crd", connection_string, log_args)

    # EC
    if "ec" in networks:
        for freq, times in zip(("daily", "hourly"), (daily_ranges, hourly_ranges)):
            for province in ("YT", "BC"):
                for time in times:
                    # EC files are named in UTC
                    time = time.astimezone(pytz.utc)
                    dl_args = [
                        "-p",
                        province,
                        "-F",
                        freq,
                        "-g" "e",
                        "-t",
                        time.strftime(time_fmt),
                    ]
                    download_and_process(dl_args, "ec", connection_string, log_args)

    # MOTI
    if "moti" in networks:

        # Query all of the stations
        stations = get_moti_stations(connection_string)

        # MoTI has an insane config where each user has a specific set
        # of stations associated with it. PCIC wants *all* the
        # stations which is too many for one request, so we have two
        # users with half of the stations. This way of requesting the
        # data will get many "skips", but at least we'll get all of
        # the data.
        for auth_key in ("moti", "moti2"):
            # Divide range into 6 day intervals
            for interval_start, interval_end in zip(
                weekly_ranges[:-1], weekly_ranges[1:]
            ):
                for station in stations:
                    start = interval_start.strftime(time_fmt)
                    end = interval_end.strftime(time_fmt)
                    dl_args = [
                        "--auth_fname",
                        auth_fname,
                        "--auth_key",
                        auth_key,
                        "-S",
                        start,
                        "-E",
                        end,
                        "-s",
                        station,
                    ]
                    download_and_process(dl_args, "moti", connection_string, log_args)

    warning_msg = {
        "disjoint": "{} cannot be infilled since the period of infilling is "
        "outside the currently offered data (the previous {}).",
        "not_contained": "{} infilling may miss some data since the requested infilling"
        " period is larger than the currently offered period of record "
        "(the previous {}).",
    }
    now = datetime.datetime.now().astimezone(tzlocal())

    # WAMR
    if "wamr" in networks:
        # Check that the interval overlaps with the last month
        last_month = (now - datetime.timedelta(days=30), now)
        # Warn if not
        if not interval_overlaps((start_time, end_time), last_month):
            warn(warning_msg["disjoint"].format("WAMR", "one month"))
        else:
            if not interval_contains((start_time, end_time), last_month):
                warn(warning_msg["not_contained"].format("WAMR", "one_month"))
            dl_args = []
            download_and_process(dl_args, "wamr", connection_string, log_args)

    # WMB
    if "wmb" in networks:
        yesterday = (now - datetime.timedelta(days=1), now)
        # Check that the interval overlaps with the last day
        # Warn if not
        if not interval_overlaps((start_time, end_time), yesterday):
            warn(warning_msg["disjoint"].format("WMB", "day"))
        else:
            if not interval_contains((start_time, end_time), yesterday):
                warn(warning_msg["not_contained"].format("WMB", "day"))
            # Run it
            dl_args = ["--auth_fname", auth_fname, "--auth_key", "wmb"]
            download_and_process(dl_args, "wmb", connection_string, log_args)

    # EC_SWOB
    if "ec_swob" in networks:
        for partner in ("bc_env_snow", "bc_tran", "bc_forestry"):
            for hour in hourly_ranges:
                hour = hour.astimezone(pytz.utc)  # EC files are named in UTC
                dl_args = ["-d", hour.strftime(time_fmt)]
                download_and_process(dl_args, partner, connection_string, log_args)


def round_datetime(d, resolution="hour", direction="down"):
    """Round a datetime up or down to the last/next hour/day

    Args:
        d (datetime.datetime): datetime value to round
        resolution (string): 'hour' or 'day'
        direction (string): 'up' or 'down'

    Returns:
       A rounded datetime
    """
    d_prime = d.replace(minute=0, second=0, microsecond=0)
    if resolution == "day":
        d_prime = d_prime.replace(hour=0)
    elif resolution == "hour":
        pass
    else:
        raise ValueError(
            f"resolution parameter can only be 'hour' or 'day' " "not '{resolution}'"
        )
    if d_prime == d:
        return d

    if direction == "up":
        kwargs = {resolution + "s": 1}
        delta = datetime.timedelta(**kwargs)
    elif direction == "down":
        delta = datetime.timedelta()
    else:
        raise ValueError(
            f"direction parameter can only be 'down' or 'up' " "not '{direction}'"
        )

    return d_prime + delta


def datetime_range(start, end, resolution="hour"):
    """Discretizes a time interval by the specified interval/resolution

    Takes a time interval, extends it to cover the full range
    (rounding the start time down and rounding the end time up), and
    yields a sequence of discrete time steps at the resolution
    provided.

    The 'week' resolution behaves slightly different since its usage
    is currently constrained to the MoTI time parameters and their
    particularities. (MoTI allows you to specify a full time range
    rather than discrete days/hours). Using the week resoultion rounds
    the beginning time step down to the nearest day and then just uses
    the end time as is. During initial testing, we found that using
    the full 7 day time range resulted in many HTTP 500 errors, so
    we're using a conservative "week" of 6 days.

    The loosely defined 'month' resolution returns 28 day intervals
    (for CRD).

    Args:
        start (datetime.datetime): The beginnng of the range
        end (datetime.datetime): The end of the range
        resolution (string): 'hour', 'day', 'week' or 'month'

    Yields:
        A sequence of datetimes, covering the range.

    """
    if resolution not in ("hour", "day", "week", "month"):
        raise ValueError
    kwargs = {
        "hour": {"hours": 1},
        "day": {"days": 1},
        "week": {"days": 6},
        "month": {"days": 28},
    }[resolution]
    step = datetime.timedelta(**kwargs)

    # Don't round down to the week... just the day and end at the actual end
    if resolution in ("week", "month"):
        start = round_datetime(start, "day", direction="down")
    # Otherwise, make a rounded timeseries to the day or hour
    else:
        start = round_datetime(start, resolution, direction="down")
        end = round_datetime(end, resolution, direction="up")

    t = start
    while t < end:
        yield t
        t += step
    yield end


def interval_contains(a, b):
    """time interval a contains time interval b"""
    return a[0] <= b[0] and a[1] >= b[1]


def interval_overlaps(a, b):
    """time interval a and b contain some overlap"""
    return max(a[0], b[0]) <= min(a[1], b[1])


def get_moti_stations(connection_string):
    """Query the database and return all native_ids available for MoTI"""
    engine = create_engine(connection_string)
    Session = sessionmaker(engine)
    sesh = Session()

    q = sesh.query(Station.native_id).join(Network).filter(Network.name == "MoTIe")
    return [native_id for (native_id,) in q.all()]
