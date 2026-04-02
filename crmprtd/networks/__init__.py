import datetime
from typing import Optional
from zoneinfo import ZoneInfo

"""Common Default functions for networks. Many do not need bespoke versions, so
they can be defined here and reused.

The interface for network_defaults should be a module with functions:

- default_log_filename(**args) -> str
- default_cache_filename(**args) -> str
- default_time(**args) -> datetime.datetime
- default_end_time(**args) -> datetime.datetime
- default_download_args(**args) -> list[str]
"""

default_timestamp_format = "%Y-%m-%dT%H:%M:%S"


# TODO: is tz_string a safe assumption to be our locality? shouldn't this really be based on OS locale?
def to_utc(d: datetime.datetime):
    if d.tzinfo is None:
        # d is not localized. Make it so.
        d = d.astimezone()
    return d.astimezone(ZoneInfo("UTC"))


def default_cache_filename(
    network_name: str,
    tag: Optional[str] = None,
    timestamp: datetime.datetime = datetime.datetime.now(),
    timestamp_format: str = default_timestamp_format,
    **_,
) -> str:
    """Return cache filename (filepath). It depends on several parameters, starting
    with the network. Its pattern is similar, but not identical, to that of the log
    filename.

    :param timestamp: Timestamp to include in filename.
    :param timestamp_format: Format for converting timestamp to string.
    :param network_name: Network name to include in filename.
    :param tag: Tag to include in filename.
    :param _: Ignored additional kw args.
    :return: Filename.
    """
    ts = timestamp.strftime(timestamp_format)
    filepath = f"~/{network_name}/cache"
    tag_prefix = f"{tag}_" if tag is not None else ""
    return f"{filepath}/{tag_prefix}{network_name}_{ts}.txt"


def default_swob_cache_filename(
    timestamp: datetime.datetime = datetime.datetime.now(),
    timestamp_format: str = default_timestamp_format,
    network_name: Optional[str] = None,
    tag: Optional[str] = None,
    **_,
) -> str:
    """Return cache filename (filepath). It depends on several parameters, starting
    with the network. Its pattern is similar, but not identical, to that of the log
    filename.

    :param timestamp: Timestamp to include in filename.
    :param timestamp_format: Format for converting timestamp to string.
    :param network_name: Network name to include in filename.
    :param tag: Tag to include in filename.
    :param _: Ignored additional kw args.
    :return: Filename.
    """
    ts = timestamp.strftime(timestamp_format)
    filepath = f"~/{network_name}/cache"
    tag_prefix = f"{tag}_" if tag is not None else ""
    return f"{filepath}/{tag_prefix}{network_name}_{ts}.xml"


def default_log_filename(
    network_name: str,
    tag: Optional[str] = None,
    **_,
):
    """Return log filename (filepath). It depends on several parameters, starting
    with the network. Its pattern is similar, but not identical, to that of the cache
    filename.
    :param network_name: Network name to include in filename.
    :param tag: Tag to include in filename.
    :param _: Ignored additional kw args.
    :return: Filename.
    """
    filepath = f"~/{network_name}/logs"
    tag_prefix = f"{tag}_" if tag is not None else ""
    return f"{filepath}/{tag_prefix}{network_name}_json.log"


def empty_default_download_args(**_):
    """Some networks do not require any special download arguments."""
    return []


def gen_default_swob_download_args(network_name: str):
    """SWOB networks follow a similar pattern, we can use a generator function to
    create a default function for each network."""

    def swob_default_download_args(time: Optional[datetime.datetime], **_):
        if time is None:
            raise ValueError(f"Network {network_name} requires a time parameter")
        ts = to_utc(time).strftime("%Y/%m/%d %H:00:00")
        return ["-d", f'"{ts}"']

    return swob_default_download_args

def default_time(**_):
    return datetime.datetime.now().astimezone()

def default_end_time(**_):
    return datetime.datetime.now().astimezone()

def default_swob_time(**_):
    # SWOB data is always for the previous hour
    return datetime.datetime.now(ZoneInfo("UTC")) - datetime.timedelta(hours=1)