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


if __name__ == "__main__":
    main()
