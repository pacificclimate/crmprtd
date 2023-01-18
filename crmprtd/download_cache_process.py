"""
This script choreographs the download and process steps (with optional data caching)
in the pipeline.

TODO: More doc.
"""

import datetime
from argparse import ArgumentParser
from typing import List

import pytz

from crmprtd import NETWORKS, add_version_arg
from crmprtd.argparse_helpers import OneAndDoneAction
from crmprtd.infill import download_and_process

# Maps a network alias to a *list* of networks (names). This allows for both groups
# and single-network aliases.
# TODO: This should probably be in a config file.
network_aliases = {
    "bch": ["bc_hydro"],
    "hourly_swobml2": [
        "bc_env_snow",
        "bc_forestry",
        "bc_tran",
        "dfo_ccg_lighthouse",
    ],
    "ytnt": [
        "nt_forestry",
        "nt_water",
        "yt_gov",
        "yt_water",
        "yt_avalanche",
        "yt_firewx",
    ],
}

network_alias_names = tuple(network_aliases.keys())


def check_network_name(network_name):
    if network_name not in NETWORKS:
        raise ValueError(f"Network name '{network_name}' is not recognized.")


def default_log_filename(
    network_name: str = None,
    tag: str = None,
    frequency: str = None,
    province: str = None,
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
    check_network_name(network_name)
    filepath = f"~/{network_name}/logs"
    if network_name in ("ec",):
        return f"{filepath}/{tag}_{province.lower()}_{frequency}_json.log"
    return f"{filepath}/{tag}_{network_name}_json.log"


def default_cache_filename(
    timestamp: datetime.datetime = datetime.datetime.now(),
    timestamp_format: str = "%Y-%m-%dT%H:%M:%S",
    network_name: str = None,
    tag: str = None,
    frequency: str = None,
    province: str = None,
    **_,
) -> str:
    """Return cache filename (filepath). It depends on several parameters, starting
    with the network. Its pattern is similar, but not identical, to that of the log
    filename.

    :param timestamp: Timestamp to include in filename.
    :param timestamp_format: Format for converting timestamp to string.
    :param network_name: Network name to include in filename.
    :param tag: Tag to include in filename.
    :param frequency: Download frequency to include in filename (network ec only).
    :param province: Province code (2 letters) to include in filename (network ec only).
    :param _: Ignored additional kw args.
    :return: Filename.
    """
    check_network_name(network_name)
    ts = timestamp.strftime(timestamp_format)
    filepath = f"~/{network_name}/cache"
    if network_name in ("ec",):
        return f"{filepath}/{tag}_{frequency}_{province.lower()}_{ts}.xml"
    if network_name in (
        "bc_env_snow",
        "bc_forestry",
        "bc_tran",
        "dfo_ccg_lighthouse",
        "nt_forestry",
        "nt_water",
        "yt_gov",
        "yt_water",
        "yt_avalanche",
        "yt_firewx",
    ):
        return f"{filepath}/{tag}_{network_name}_{ts}.xml"
    return f"{filepath}/{tag}_{network_name}_{ts}.txt"


def log_args(log_filename: str = None, **kwargs) -> List[str]:
    """Return logging args. Only the log filename depends on the arguments."""
    return [
        "-L",
        "~/logging.yaml",
        "--log_filename",
        log_filename or default_log_filename(**kwargs),
    ]


def to_utc(d: datetime.datetime, tz_string: str = "Canada/Pacific"):
    if d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None:
        # d is not localized. Make it so.
        tz = pytz.timezone(tz_string)
        d = tz.localize(d)
    return d.astimezone(pytz.utc)


def download_args(
    network_name: str = None,
    frequency: str = None,
    province: str = None,
    time: datetime.datetime = None,  # TODO: use now()?
    start_time: datetime.datetime = None,
    **_,
) -> List[str]:
    """Return command-line args for download phase. They depend on the network and
    other arguments.

    :param time:
    :param start_time:
    :param network_name: Network name.
    :param _: Remainder args. Passed through.
    :return: List of download args.
    """
    check_network_name(network_name)

    common_args = f"-N {network_name} ".split()
    net_args = None

    # Set net_args per network.
    if network_name == "bc_hydro":
        net_args = "-f sftp2.bchydro.com -F pcic -S ~/.ssh/id_rsa".split()
    if network_name == "crd":
        net_args = f"--auth_fname ~/.rtd_auth.yaml --auth_key={network_name}".split()
    if network_name == "ec":
        net_args = f"-p {province.lower()} -F {frequency}".split()
    if network_name in (
        "bc_env_snow",
        "bc_forestry",
        "bc_tran",
        "dfo_ccg_lighthouse",
        "nt_forestry",
        "nt_water",
        "yt_gov",
        "yt_water",
        "yt_avalanche",
        "yt_firewx",
    ):
        ts = to_utc(time).strftime("%Y/%m/%d %H:00:00")
        net_args = ["-d", f'"{ts}"']
    if network_name == "moti":
        net_args = f"-u https://prdoas5.apps.th.gov.bc.ca/saw-data/sawr7110 --auth_fname ~/.rtd_auth.yaml --auth_key={network_name}".split()
    if network_name == "wamr":
        net_args = []
    if network_name == "wmb":
        net_args = f"--auth_fname ~/.rtd_auth.yaml --auth_key={network_name}".split()

    assert net_args is not None
    return common_args + net_args


def alias_to_networks(network_alias: str):
    return network_aliases[network_alias]


def dispatch_network(
    cache_filename: str = None, connection_string: str = None, **kwargs
) -> None:
    """
    Dispatch a single network to the download-and-process pipeline.

    :param cache_filename: Custom cache filename.
    :param connection_string: Database connection string for "process" step.
    :param kwargs: Remaining args, passed through to various subfunctions. Note that
        network name is one of these args.
    :return: None. Side effect: Download and process network specified in args.
    """
    network_name = kwargs["network_name"]
    check_network_name(network_name)

    if network_name == "ec":
        for province in ("BC", "YT"):
            download_and_process(
                network_name=network_name,
                log_args=log_args(**kwargs, province=province),
                download_args=download_args(**kwargs, province=province),
                cache_filename=(
                    cache_filename
                    or default_cache_filename(**kwargs, province=province)
                ),
                connection_string=connection_string,
            )
    elif network_name in (
        "bc_env_snow",
        "bc_forestry",
        "bc_tran",
        "dfo_ccg_lighthouse",
        "nt_forestry",
        "nt_water",
        "yt_gov",
        "yt_water",
        "yt_avalanche",
        "yt_firewx",
    ):
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        download_and_process(
            network_name=network_name,
            log_args=log_args(**kwargs),
            download_args=download_args(**kwargs, time=an_hour_ago),
            cache_filename=(
                cache_filename
                or default_cache_filename(**kwargs, timestamp=an_hour_ago)
            ),
            connection_string=connection_string,
        )
    else:
        now = datetime.datetime.now()
        download_and_process(
            network_name=network_name,
            log_args=log_args(**kwargs),
            download_args=download_args(**kwargs, time=now),
            cache_filename=(
                cache_filename or default_cache_filename(**kwargs, timestamp=now)
            ),
            connection_string=connection_string,
        )


def dispatch_network_alias(network_alias: str = None, **kwargs) -> None:
    """
    Dispatch each network defined by an alias.

    :param network_alias: Alias name.
    :param kwargs: Remaining args, passed through.
    :return: None.
    """
    assert network_alias in network_alias_names
    for network_name in alias_to_networks(network_alias):
        dispatch_network(network_name=network_name, **kwargs)


def dispatch(network: str = None, **kwargs) -> None:
    """
    Dispatch a network or a network alias.

    :param network: Network name or network alias name.
    :param kwargs: Remain args, passed through.
    :return: None.
    """
    assert network is not None
    if network in network_alias_names:
        dispatch_network_alias(network_alias=network, **kwargs)
    elif network in NETWORKS:
        dispatch_network(network_name=network, **kwargs)
    else:
        raise ValueError(
            f"Network argument '{network}' is not a valid network name or alias"
        )


def describe_network(network):
    """Return a string describing `network`, which may be a network name or alias."""
    if network in NETWORKS:
        return f"'{network}' is the name of a single network"
    if network in network_alias_names:
        return (
            f"'{network}' is the name of a network alias, which translates to the "
            f"following network names: {', '.join(network_aliases[network])}"
        )
    return f"'{network}' is not a known network name or alias"


def main(arglist: List[str] = None) -> None:
    """
    Mainline for script.

    Note: This script allows for only two options:
    1. Download data and cache only (omit database connection string).
    2. Download data, cache it, and process it.

    :param arglist: Argument list to be processed by argparse. This eases testing;
        if None then sys.argv is used.
    :return: None.
    """

    parser = ArgumentParser(
        description="""
            The download-cache-process dispatcher. Starts two subprocesses
            running crmprtd_download and crmprtd_process with appropriate arguments,
            pipes the first into the second, and caches the downloaded data.
        """
    )

    add_version_arg(parser)

    parser.add_argument(
        "-D",
        "--describe",
        nargs=1,
        choices=NETWORKS + network_alias_names,
        action=OneAndDoneAction,
        function=describe_network,
        help="Describe a network name or alias",
    )

    parser.add_argument(
        "-N",
        "--network",
        choices=NETWORKS + network_alias_names,
        required=True,
        help=(
            "Network identifier (a network name or network alias) from which to "
            "download observations. A network alias can stand for one or more "
            "individual networks (e.g., 'ytnt' stands for many networks)."
        ),
    )

    # Log and cache filenames

    parser.add_argument(
        "-T",
        "--tag",
        help="Tag for forming default names for log and cache files",
    )
    parser.add_argument(
        "--log_filename",
        help=(
            "Filename for log file. (If omitted, use default filename generated "
            "from network name, tag, and other parameters.)"
        ),
    )
    parser.add_argument(
        "--cache_filename",
        help=(
            "Filename for cache file. (If omitted, use default filename generated "
            "from network name, tag, and other parameters.)"
        ),
    )

    # Processing step

    parser.add_argument(
        "-c",
        "--connection_string",
        help=(
            "Connection string for target database. "
            "If absent, processing step is not performed."
        ),
    )

    args, _ = parser.parse_known_args(arglist)

    # Network-dependent args
    if args.network == "ec":
        parser.add_argument(
            "-F",
            "--frequency",
            choices=["daily", "hourly"],
            required=True,
            help="Frequency of download (network ec only)",
        )
        args = parser.parse_args(arglist)

    # TODO: Add network-dependent time arg here? Currently it is hardwired in code to
    #  "now".

    dispatch(**vars(args))


if __name__ == "__main__":
    main()
