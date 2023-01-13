import datetime
from argparse import ArgumentParser
from typing import List

from crmprtd import add_version_arg, get_version, NETWORKS
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


def log_filename(
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
    if network_name not in NETWORKS:
        raise ValueError(f"Network name '{network_name}' is not recognized.")
    if network_name in ("ec",):
        return f"~/{network_name}/logs/{tag}_{province.lower()}_{frequency}_json.log"
    if network_name in ("wmb",):
        # Oh, yes, this one has to be a special snowflake.
        return f"~/{network_name}/logs/{tag}_mof_json.log"
    return f"~/{network_name}/logs/{tag}_{network_name}_json.log"


def cache_filename(
    timestamp: datetime.datetime = datetime.datetime.now(),
    timestamp_format : str = "%Y-%m-%dT%H:%M:%S",
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
    if network_name not in NETWORKS:
        raise ValueError(f"Network name '{network_name}' is not recognized.")

    ts = timestamp.strftime(timestamp_format)
    if network_name in ("ec",):
        return f"~/{network_name}/download/{tag}_{frequency}_{province.lower()}_{ts}.xml"
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
        return f"~/{network_name}/cache/{tag}_{network_name}_{ts}.xml"
    if network_name in ("wmb",):
        return f"~/{network_name}/download/{tag}_{network_name}_{ts}.txt"
    return f"~/{network_name}/cache/{tag}_{network_name}_{ts}.txt"


def log_args(**kwargs):
    """Return logging args. Only the log filename depends on the arguments."""
    return [
        "-L",
        "~/logging.yaml",
        "--log_filename",
        log_filename(**kwargs),
    ]


def download_args(network_name=None, **_):
    """Return args for download phase. They depend on the network and other arguments."""
    return []


def alias_to_networks(network_alias: str):
    return network_aliases[network_alias]


def dispatch_network(connection_string: str = None, **kwargs) -> None:
    """
    Dispatch a single network to the download-and-process pipeline.

    :param connection_string: Database connection string for "process" step.
    :param kwargs: Remaining args, passed through to various subfunctions. Note that
        network name is one of these args.
    :return: None. Side effect: Download and process network specified in args.
    """
    network_name = kwargs["network_name"]
    assert network_name in NETWORKS
    print(
        f"dispatching network {network_name} with connection_string={connection_string}",
        kwargs,
    )
    return

    # TODO: Some network-dependent stuff here; see ec, moti.
    download_and_process(
        network_name=network_name,
        log_args=log_args(**kwargs),
        download_args=download_args(**kwargs),
        cache_filename=cache_filename(**kwargs),
        connection_string=connection_string,
    )


def dispatch_alias(network_alias: str = None, **kwargs) -> None:
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
    del kwargs["version"]
    if network in network_alias_names:
        dispatch_alias(network_alias=network, **kwargs)
    elif network in NETWORKS:
        dispatch_network(network_name=network, **kwargs)
    else:
        raise ValueError(
            f"Network argument '{network}' is neither a valid network name nor an alias"
        )


def main(arglist: List[str] = None) -> None:
    """
    Mainline for dispatcher.

    :param arglist: Argument list to be processed by argparse. This eases testing;
        if None then sys.argv is used.
    :return: None.
    """

    parser = ArgumentParser(
        description="""
            Dispatcher for download-and-process pipeline. Starts two subprocesses
            running crmprtd_download and crmprtd_process with appropriate arguments,
            pipes the first into the second, and caches the downloaded data.
        """
    )

    # Don't force user to provide normally required arguments for this case.
    add_version_arg(parser)
    args, _ = parser.parse_known_args(arglist)
    if args.version:
        print(get_version())
        return

    parser.add_argument(
        "-N",
        "--network",
        choices=NETWORKS + network_alias_names,
        required=True,
        help=(
            "Network identifier (may designate more than one group) from "
            "which to download observations"
        ),
    )
    parser.add_argument(
        "-T",
        "--tag",
        required=True,
        help="Tag for naming log and cache files",
    )
    parser.add_argument(
        "-c",
        "--connection_string",
        help="Connection string for target database",
        required=True,
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

    dispatch(**vars(args))


if __name__ == "__main__":
    main()
