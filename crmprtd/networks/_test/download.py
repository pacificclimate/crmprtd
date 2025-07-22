"""
A test downloader that does nothing.
"""

import logging
import os
from argparse import ArgumentParser
from typing import List

from crmprtd import (
    setup_logging,
)

log = logging.getLogger(__name__)


def download():  # pragma: no cover
    # Could write something to sys.stdout
    log.info(f"environment {os.environ}")
    log.info("Network _test: no-op")


def main(
    arglist: List[str] = None, parent_parser: ArgumentParser = None
) -> None:  # pragma: no cover
    """Downloads nothing from nowhere :)

    Side effect: Does nothing and writes nothing to STDOUT.

    :param arglist: Argument list (for testing; default is to parse from sys.argv).
    :param parent_parser: Argument parser common to all network downloads.
    """
    parser = ArgumentParser(parents=[parent_parser], description=globals()["__doc__"])
    args = parser.parse_args(arglist)

    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd.networks._test",
    )

    download()


if __name__ == "__main__":
    main()
