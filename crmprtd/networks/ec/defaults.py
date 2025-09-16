import datetime
from typing import Optional
from crmprtd.networks import default_timestamp_format


def default_cache_filename(
    timestamp: datetime.datetime = datetime.datetime.now(),
    timestamp_format: str = default_timestamp_format,
    network_name: Optional[str] = None,
    tag: Optional[str] = None,
    frequency: Optional[str] = None,
    province: Optional[str] = None,
    **_,
) -> str:
    """Return cache filename (filepath). It depends on several parameters, starting
    with the network. Its pattern is similar, but not identical, to that of the log
    filename.

    EC network uniquely requires frequency and province to be part of the filename.

    :param timestamp: Timestamp to include in filename.
    :param timestamp_format: Format for converting timestamp to string.
    :param network_name: Network name to include in filename.
    :param tag: Tag to include in filename.
    :param frequency: Download frequency to include in filename (network ec only).
    :param province: Province code (2 letters) to include in filename (network ec only).
    :param _: Ignored additional kw args.
    :return: Filename.
    """
    ts = timestamp.strftime(timestamp_format)
    filepath = f"~/{network_name}/cache"
    tag_prefix = f"{tag}_" if tag is not None else ""
    assert frequency is not None
    assert province is not None
    return f"{filepath}/{tag_prefix}{frequency}_{province.lower()}_{ts}.xml"


def default_log_filename(
    network_name: Optional[str] = None,
    tag: Optional[str] = None,
    frequency: Optional[str] = None,
    province: Optional[str] = None,
    **_,
):
    """Return log filename (filepath). It depends on several parameters, starting
    with the network. Its pattern is similar, but not identical, to that of the cache
    filename.

    :param network_name: Network name to include in filename.
    :param tag: Tag to include in filename.
    :param frequency: Download frequency to include in filename (network ec only).
    :param province: Province code (2 letters) to include in filename (network ec only).
    :param _: Ignored additional kw args.
    :return: Filename.
    """
    filepath = f"~/{network_name}/logs"
    tag_prefix = f"{tag}_" if tag is not None else ""
    assert frequency is not None
    assert province is not None
    return f"{filepath}/{tag_prefix}{province.lower()}_{frequency}_json.log"


def default_download_args(province: Optional[str], frequency: Optional[str], **_):
    if province is None or frequency is None:
        raise ValueError("EC network requires both province and frequency")
    return f"-p {province.lower()} -F {frequency}".split()

def default_time(**_):
    ## EC network uses UTC time
    return datetime.datetime.now(datetime.timezone.utc)

def default_end_time(**_):
    ## EC network uses UTC time
    return datetime.datetime.now(datetime.timezone.utc)