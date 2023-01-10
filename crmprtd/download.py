"""
Single entrypoint for downloads. A network argument is always required, and it
determines which module (e.g., ec, moti) provides the download function.

Function main is invoked by the command line. It defines an argument parser, and on
that parser it defines a single argument for the network. It obtains the network-
specific download module, and invokes that module's `main` function with the parser as
an argument. Each `main` function defines its own set of arguments, parses them, and
proceeds from there.

This approach has pros and cons. Pros:
- Pros: Minimal changes existing code and of scripts that use it.
- Cons: Harder to test end-to-end.

An alternative, not implemented, would be to define a common set of arguments in
this module, parse them, and pass them to a network download module's `download`
function, or a main-like wrapper for it. Pros and cons:
- Pros: Uniformity of arguments. Easier to test end-to-end (?).
- Cons: Significant changes to existing code. Greater complexity. Significant changes
to scripts that use it.
"""
from typing import List
from importlib import import_module
from argparse import ArgumentParser

from crmprtd import (
    add_version_arg,
    add_logging_args,
    NETWORKS,
)


def get_download_module(network):
    return import_module(f"crmprtd.{network}.download")


# TODO: Abandoned approach. Remove.
# def download(network=None, **kwargs):
#     download_module = get_download_module(network)
#     download_module.download(**kwargs)


def main(arglist: List[str] = None):
    parser = ArgumentParser(add_help=False)

    # Basic args
    add_version_arg(parser)
    add_logging_args(parser)

    # Network arg
    parser.add_argument(
        "-N",
        "--network",
        required=True,
        choices=NETWORKS,
        help="Network from which to download observations",
    )

    args = parser.parse_args(arglist)

    # Download module will define network-specific args.
    download_module = get_download_module(args.network)
    download_module.main(arglist=arglist, parent_parser=parser)

    # TODO: Abandoned approach. Remove.
    # # Date args (almost all networks)
    # # TOOD: Fix help on defaults.
    # parser.add_argument(
    #     "-s",
    #     "--start_date",
    #     help=(
    #         "Optional start time to use for downloading "
    #         "(interpreted with dateutil.parser.parse). "
    #         "Defaults to one month prior to now."
    #     ),
    # )
    # parser.add_argument(
    #     "-e",
    #     "--end_date",
    #     help=(
    #         "Optional end time to use for downloading "
    #         "(interpreted with dateutil.parser.parse). "
    #         "Defaults to now."
    #     ),
    # )
    # parser.add_argument(
    #     "-d",
    #     "--date",
    #     help=(
    #         "Alternate date to use for downloading "
    #         "(interpreted with dateutil.parser.parse)."
    #         "Defaults to now."
    #         "Equivalent to --start_date"
    #     ),
    # )
    # parser.add_argument(
    #     "-t",
    #     "--time",
    #     help=(
    #         "Alternate *UTC* time to use for downloading "
    #         "(interpreted using dateutil.parser.parse)."
    #         "Defaults to the previous hour/day (depending on --frequency)."
    #         "Equivalent to --start_date"
    #     ),
    # )
    #
    # # FTP args (bc_hydro, wamr, wmb)
    # parser.add_argument(
    #     "-u", "--username", default="pcic", help="Username for the ftp server "
    # )
    # parser.add_argument(
    #     "-S",
    #     "--ftp_server",
    #     default="sftp2.bchydro.com",
    #     help="Full uri to BC Hydro's ftp server",
    # )
    # parser.add_argument(
    #     "-D",
    #     "--ftp_dir",
    #     default=("pcic"),
    #     help="FTP Directory containing BC hydro's data files",
    # )
    # parser.add_argument(
    #     "-k",
    #     "--ssh_private_key",
    #     help="Path to file with SSH private key",
    # )
    #
    # # Frequency arg (ec only)
    # parser.add_argument(
    #     "-F",
    #     "--frequency",
    #     choices=["daily", "hourly"],
    #     help="daily|hourly",
    # )
    #
    # # Threshold arg (ec only)
    # parser.add_argument(
    #     "-T",
    #     "--threshold",
    #     default=1000,
    #     help=(
    #         "Distance threshold (in meters) to use when "
    #         "matching stations. Stations are considered a "
    #         "match if they have the same id, name, and are "
    #         "within this threshold"
    #     ),
    # )
    #
    # # Base URL (ec, moti)
    # parser.add_argument(
    #     "-b",
    #     "--base_url",
    #     # TODO: Default depends on network.
    #     # ec: default="https://dd.weather.gc.ca",
    #     # moti: default="https://prdoas5.apps.th.gov.bc.ca/saw-data/sawr7110",
    #     help="Base URL for download service",
    # )
    #
    # # Station ID (moti)
    # parser.add_argument(
    #     "-i", "--station_id", default=None, help="Station ID for which to download data"
    # )
    #
    # # Language (ec)
    # parser.add_argument(
    #     "-g",
    #     "--language",
    #     default="e",
    #     choices=["e", "f"],
    #     help="'e' (english) | 'f' (french)",
    # )
    #
    # # Province (ec)
    # parser.add_argument("-p", "--province", help="2 letter province code")
    #
    # args = parser.parse_args(args)
    #
    # setup_logging(
    #     args.log_conf, args.log_filename, args.error_email, args.log_level, "crmprtd"
    # )
    #
    # if args.version:
    #     print(get_version())
    #     return
    #
    # arg_dict = vars(args)
    # reduced_args = {k: v for k, v in arg_dict.items()}
    #
    # download(**reduced_args)


if __name__ == "__main__":
    main()
