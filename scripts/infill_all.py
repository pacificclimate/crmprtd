"""Infill crmprtd data for *all* networks for some time range.

This script can be used to infill some missed data for any set of
networks that are available in crmprtd. The script is minimally
configurable for ease of use. Simply give it a start time and end
time, and based on the network, it will compute whether it can make a
request for that time range. If it can, it will go out and download
all of the data for that time range, and the process it into the
database.

Only four parameters are required: a start time, end time, auth
details (for MoTI and WMB) and a database connection. Optionally you
can configure the loggging, and select a subset of available networks
to infill.
"""

from argparse import ArgumentParser
import datetime
import itertools

from dateutil.tz import tzlocal

from crmprtd import add_logging_args, setup_logging, add_version_arg, get_version
from crmprtd.infill import infill


def main():
    desc = globals()["__doc__"]
    parser = ArgumentParser(description=desc)
    add_version_arg(parser)
    parser.add_argument(
        "-S",
        "--start_time",
        help=(
            "Alternate time to use for downloading "
            "(interpreted with "
            "strptime(format='Y/m/d H:M:S')."
        ),
    )
    parser.add_argument(
        "-E",
        "--end_time",
        help=(
            "Alternate time to use for downloading "
            "(interpreted with "
            "strptime(format='Y/m/d H:M:S')."
        ),
    )
    parser.add_argument(
        "-a",
        "--auth_fname",
        help="Yaml file with plaintext usernames/passwords. "
        "For simplicity the auth keys are *not* "
        "configurable (unlike the download scripts. The "
        "supplied file must contain keys with names "
        "'moti', 'moti2' and 'wmb' if you want to infill "
        "those networks.",
    )
    parser.add_argument(
        "-c", "--connection_string", help="PostgreSQL connection string"
    )
    parser.add_argument(
        "-N",
        "--networks",
        nargs="*",
        default="crd ec moti wamr wmb ec_swob",
        help="Set of networks for which to infill",
    )

    parser = add_logging_args(parser)
    args = parser.parse_args()

    if args.version:
        print(get_version())
        return

    log_args = [
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "infill_all",
    ]
    setup_logging(*log_args)

    fmt = "%Y/%m/%d %H:%M:%S"
    s = datetime.datetime.strptime(args.start_time, fmt).astimezone(tzlocal())
    e = datetime.datetime.strptime(args.end_time, fmt).astimezone(tzlocal())

    log_args = [(x, y) for (x, y) in zip(["-L", "-l", "-m", "-o"], log_args) if y]
    log_args = list(itertools.chain(*log_args))

    infill(args.networks, s, e, args.auth_fname, args.connection_string, log_args)


if __name__ == "__main__":
    main()
