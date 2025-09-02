import datetime
import pytz
from typing import Optional


def to_utc(d: datetime.datetime, tz_string: str = "Canada/Pacific"):
    if d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None:
        # d is not localized. Make it so.
        tz = pytz.timezone(tz_string)
        d = tz.localize(d)
    return d.astimezone(pytz.utc)


def default_cache_filename(
    time: datetime.datetime = datetime.datetime.now(),
    timestamp_format: str = "%Y-%m-%dT%H:%M:%S",
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
    ts = time.strftime(timestamp_format)
    filepath = f"~/{network_name}/cache"
    tag_prefix = f"{tag}_" if tag is not None else ""
    return f"{filepath}/{tag_prefix}{network_name}_{ts}.txt"


def default_swob_cache_filename(
    timestamp: datetime.datetime = datetime.datetime.now(),
    timestamp_format: str = "%Y-%m-%dT%H:%M:%S",
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
    network_name: Optional[str] = None,
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
    return []


def gen_default_swob_download_args(network_name: str):
    def swob_default_download_args(time: Optional[datetime.datetime], **_):
        if time is None:
            raise ValueError(f"Network {network_name} requires a time parameter")
        ts = to_utc(time).strftime("%Y/%m/%d %H:00:00")
        return ["-d", f'"{ts}"']

    return swob_default_download_args
