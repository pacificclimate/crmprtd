import re
import logging
import datetime
from typing import List, TextIO, Optional
from subprocess import run, PIPE

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pycds import Station, Network
from dateutil.tz import tzlocal
import pytz

from crmprtd import expand_path


logger = logging.getLogger(__name__)


def chain_subprocesses(
    commands: List[List[str]],
    run_kwargs=None,
    final_destination: Optional[TextIO] = None,
) -> None:
    """
    Chain a series of commands by starting a subprocess for each and piping the output
    of each one successively to the next. If the output (stdout) of the final command is
    to be redirected (written) to a file, set `final_destination` to a file object.

    :param commands: List of commands to be run in a subprocess and changed. A command
        itself is a list of strings, and is the main argument for subprocess.run.
    :param run_kwargs: Passed through to subprocesses.run. If None, the default value
        {"shell": True, "check": True} is used.
    :param final_destination: Optional text file object to which the output of the
        last process can be directed.
    :return: None.

    Side effects: Run the commands.
    """
    if run_kwargs is None:
        run_kwargs = {"shell": True, "check": True}
    shell = run_kwargs.get("shell", False)
    proc = None
    for i, command in enumerate(commands):
        proc = run(
            # Command must be a single string if shell is True
            " ".join(command) if shell else command,
            **run_kwargs,
            input=(proc and proc.stdout),
            stdout=PIPE if i < len(commands) - 1 else final_destination,
        )


def download_and_process(
    network_name: str,
    log_args: List[str],
    download_args: List[str],
    cache_filename: Optional[str] = None,
    connection_string: Optional[str] = None,
    dry_run: bool = True,
):
    """
    Start subprocesses as necessary to perform download-and-process pipeline.
    The download step is always performed (using script `crmprtd_download`).
    The result of downloading can optionally be directed to a cache file (as well as
        processed if the process step is requested).
    The process step is optionally performed (using script `crmprtd_process`).

    :param network_name: Name of network to download.
    :param log_args: Configuration for application logging.
    :param download_args: Args to be passed to crmprtd_download.
    :param cache_filename: Name of file in which to cache downloaded data. If this
        arg is None, data is not cached even if it is processed.
    :param connection_string: Database connection string for process step. If this
        arg is none, the process step is skipped.
    :param dry_run: If true, print commands but don't run them.
    :return:
    """
    # Ensure this method was not invoked sloppily.
    assert dry_run is not None

    do_cache = cache_filename is not None
    do_process = connection_string is not None
    do_download = do_cache or do_process

    if not do_download:
        logger.warning(
            f"Network {network_name}: Data is to be neither cached nor processed. "
            f"Nothing to do."
        )
    
    if not do_process:
        logger.info(
            f"Network {network_name}: Data is to be downloaded but not processed."
        )

    # Build up commands to be chained in this list
    commands = []

    def add_command(command):
        message = " ".join(command)
        message = re.sub(r"postgresql://(.*?)@", r"postgresql://", message)
        logger.debug(message)
        commands.append(command)

    # Set up download step
    if do_download:
        add_command(["crmprtd_download"] + download_args + log_args)

    # Set up process step.
    if do_process:
        if do_cache:
            add_command(["tee", cache_filename])
        add_command(
            [
                "crmprtd_process",
                "-N",
                network_name,
                "-c",
                connection_string,
            ]
            + log_args,
        )

    if dry_run:
        message = " | ".join([" ".join(command) for command in commands]) + (
            f" > {cache_filename}" if do_cache and not do_process else ""
        )
        message = re.sub(r"postgresql://(.*?)@", r"postgresql://", message)
        print(message)
        return

    chain_subprocesses(
        commands,
        final_destination=(
            open(expand_path(cache_filename), "w")
            if do_cache and not do_process
            else None
        ),
    )


def infill(
    networks,
    start_time,
    end_time,
    auth_fname,
    connection_string,
    log_args,
    dry_run=False,
):
    """Set up and delegate all infilling processes to scripts
    crmprtd_download and crmprtd_process, invoked in a subprocess.
    """

    # Compute lists of "discretized" time periods between start and end time, for each
    # important resolution: month, week, day, hour. Notes:
    # - A "month" is 28 days.
    # - A "week" is 6 days. (7-day intervals were too much data for some services.)
    # - "Day" and "hour" have their usual meanings.
    monthly_ranges = list(datetime_range(start_time, end_time, resolution="month"))
    weekly_ranges = list(datetime_range(start_time, end_time, resolution="week"))
    daily_ranges = list(datetime_range(start_time, end_time, resolution="day"))
    hourly_ranges = list(datetime_range(start_time, end_time, resolution="hour"))

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
            download_and_process(
                network_name="crd",
                log_args=log_args,
                download_args=dl_args,
                connection_string=connection_string,
                dry_run=dry_run,
            )

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
                    download_and_process(
                        network_name="ec",
                        log_args=log_args,
                        download_args=dl_args,
                        connection_string=connection_string,
                        dry_run=dry_run,
                    )

    # MOTI
    if "moti" in networks:
        # Query all existing stations
        stations = get_moti_stations(connection_string)

        # MoTI has an insane config where each user has a specific set
        # of stations associated with it. PCIC wants *all* the
        # stations which is too many for one request, so we have two
        # users with half of the stations. This way of requesting the
        # data will get many "skips", but at least we'll get all the data.
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
                    download_and_process(
                        network_name="moti",
                        log_args=log_args,
                        download_args=dl_args,
                        connection_string=connection_string,
                        dry_run=dry_run,
                    )

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
            logger.warning(warning_msg["disjoint"].format("WAMR", "one month"))
        else:
            if not interval_contains((start_time, end_time), last_month):
                logger.warning(warning_msg["not_contained"].format("WAMR", "one_month"))
            dl_args = []
            download_and_process(
                network_name="wamr",
                log_args=log_args,
                download_args=dl_args,
                connection_string=connection_string,
                dry_run=dry_run,
            )

    # WMB
    if "wmb" in networks:
        yesterday = (now - datetime.timedelta(days=1), now)
        # Check that the interval overlaps with the last day
        # Warn if not
        if not interval_overlaps((start_time, end_time), yesterday):
            logger.warning(warning_msg["disjoint"].format("WMB", "day"))
        else:
            if not interval_contains((start_time, end_time), yesterday):
                logger.warning(warning_msg["not_contained"].format("WMB", "day"))
            # Run it
            dl_args = ["--auth_fname", auth_fname, "--auth_key", "wmb"]
            download_and_process(
                network_name="wmb",
                log_args=log_args,
                download_args=dl_args,
                connection_string=connection_string,
                dry_run=dry_run,
            )

    # EC_SWOB
    if "ec_swob" in networks:
        for partner in ("bc_env_snow", "bc_tran", "bc_forestry"):
            for hour in hourly_ranges:
                hour = hour.astimezone(pytz.utc)  # EC files are named in UTC
                dl_args = ["-d", hour.strftime(time_fmt)]
                download_and_process(
                    network_name=partner,
                    log_args=log_args,
                    download_args=dl_args,
                    connection_string=connection_string,
                    dry_run=dry_run,
                )


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
            f"resolution parameter can only be 'hour' or 'day' not '{resolution}'"
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
    rather than discrete days/hours). Using the week resolution rounds
    the beginning time step down to the nearest day and then just uses
    the end time as is.

    During initial testing, we found that using the full 7 day time range
    resulted in many HTTP 500 errors, so we're using a conservative "week" of 6 days.

    The loosely defined 'month' resolution returns 28-day intervals
    (for use by CRD).

    Args:
        start (datetime.datetime): The beginning of the range
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
