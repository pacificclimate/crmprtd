"""The crmprtd ("CRMP Real Time Daemon) package

This crmprtd package is package written to perform regular, periodic
weather data acquisition from a variety of government agencies
(i.e. "networks) for long-term climate monitoring.

CRMP stands for "Climate Related Monitoring Program", the iniative by
the province of BC to jointly pool the partners' weather data. RTD
stands for "real-time daemon"), an unfortunate name since data
acquisition does not happen in real time and its programs are never
run as a daemon (at most, they are run as hourly cron jobs). But, hey,
that's the name and who's gonna change it?

The package operates a data pipeline of four phases: Download,
Normalize, Align, and Insert. The Download and Normalize phases are
specific to each network's data formats and time freqency. The Align
and Insert are common across all networks.

Download: This phase consists of polling a specific network resource
(FTP/HTTP site), downloading and saving a file that contains plain
text weather observations. The resources required are access to the
network, resource URIs, authentication details, and storage. This
phase needs to be scheduled at regular intervals (depending on the
network), and may be parametrized by date if supported by the network
(i.e. some networks allow you to select dates in the recent past).

Normalize: This phase consists of performing network specific text
transformations and extraction of information to the weather
observations. This may include XML XSLT transformations, unit or
variable name rewrites according to mapping rules, etc. The input to
this phase is an open file-like object opened in binary mode
(https://docs.python.org/3/library/io.html#binary-i-o) (e.g. a BytesIO
object or sys.stdin.buffer) and the output is simply a stream of
tuples (time, val, variable name, unit, network name, station id, lat,
lon) in native types. The idea of this phase is that it requires no
access to the database, just network specific knowledge.

Align: This phase consists of performing database consistency checks
required to insert the incoming data records. Do the stations already
exist or do we need to create them? Do the variables exist or can we
create them? Etc. The input is a stream tuples and the output is a
stream of pycds.Obs objects. This phase is common to all networks.

Insert: This phase simply consists of doing a mass insert of
observations into the database. The phase needs to handle any unique
constraint errors, and track and report on the successes and
failures. This phase needs to manage the database transactions for
speed and reliability. This phase is common to all networks.
"""

import logging
import logging.config
import os.path

from importlib.metadata import version
from importlib.resources import files
from collections import namedtuple

from crmprtd.argparse_helpers import OneAndDoneAction

SWOB_PARTNERS = (
    "bc_env_aq",
    "bc_env_snow",
    "bc_forestry",
    "bc_riotinto",
    "bc_tran",
    "nt_forestry",
    "nt_water",
    "yt_gov",
    "yt_water",
    "yt_firewx",
    "yt_avalanche",
    "dfo_ccg_lighthouse",
)

NETWORKS = SWOB_PARTNERS + ("bc_hydro", "crd", "ec", "moti", "wamr", "wmb", "_test")

Row = namedtuple(
    "Row",
    "time val variable_name unit network_name station_id lat lon",
)


# This method for --version avoids an error in testing that is provoked by using the
# action='version' method. Reason for error unknown.
def add_version_arg(parser):
    parser.add_argument(
        "--version",
        action=OneAndDoneAction,
        nargs=0,
        function=get_version,
        help="Show version number and exit",
    )
    return parser


def get_version():
    return version("crmprtd")


def add_logging_args(parser):
    parser.add_argument(
        "-L",
        "--log_conf",
        default=None,
        help="YAML file to use to override the default logging configuration",
    )
    parser.add_argument(
        "-l", "--log_filename", default=None, help="Override the default log filename"
    )
    parser.add_argument(
        "-o",
        "--log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=(
            "Set log level: DEBUG, INFO, WARNING, ERROR, "
            "CRITICAL.  Note that debug output by default "
            "goes directly to file"
        ),
    )
    parser.add_argument(
        "-m",
        "--error_email",
        default=None,
        help=(
            "Override the default e-mail address to which "
            "the program should report critical errors"
        ),
    )
    return parser


# TODO: What is a "common" argument and what are phase-specific arguments needs to be
#   reviewed. There are several arguments specific to the process phase here; others
#   specific to it are in add_process_arguments.
def common_script_arguments(parser):  # pragma: no cover
    parser.add_argument(
        "-c", "--connection_string", help="PostgreSQL connection string"
    )
    parser.add_argument(
        "-D",
        "--diag",
        default=False,
        action="store_true",
        help="Turn on diagnostic mode (no commits)",
    )
    parser.add_argument(
        "-L",
        "--log_conf",
        default=None,
        help="YAML file to use to override the default logging configuration",
    )
    parser.add_argument(
        "-l", "--log_filename", default=None, help="Override the default log filename"
    )
    parser.add_argument(
        "-o",
        "--log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=(
            "Set log level: DEBUG, INFO, WARNING, ERROR, "
            "CRITICAL.  Note that debug output by default "
            "goes directly to file"
        ),
    )
    parser.add_argument(
        "-m",
        "--error_email",
        default=None,
        help=(
            "Override the default e-mail address to which "
            "the program should report critical errors"
        ),
    )
    parser.add_argument(
        "-C",
        "--cache_file",
        help="Full path of file in which to put downloaded observations",
    )
    parser.add_argument("-i", "--input_file", help="Input file to process")
    parser.add_argument(
        "--sample_size",
        type=int,
        default=50,
        help=(
            "Number of samples to be taken from observations when searching for "
            "duplicates to determine how to handle ADAPTIVE insertion strategy"
        ),
    )
    return parser


def add_common_auth_arguments(parser):  # pragma: no cover
    parser.add_argument(
        "--auth_fname", help="Yaml file with plaintext usernames/passwords"
    )
    parser.add_argument(
        "--auth_key", help="Top level key which user/pass are stored in yaml file."
    )
    parser.add_argument(
        "--username", help="The username for data requests. Overrides auth file."
    )
    parser.add_argument(
        "--password", help="The password for data requests. Overrides auth file."
    )
    return parser


def expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))


def setup_logging(log_conf, log_filename, error_email, log_level, name):
    import yaml

    if log_conf:
        with open(expand_path(log_conf), "rb") as f:
            base_config = yaml.safe_load(f)
    else:
        with (files("crmprtd") / "data/logging.yaml").open("rb") as f:
            base_config = yaml.safe_load(f)

    if log_filename:
        base_config["handlers"]["file"]["filename"] = log_filename

    if error_email:
        base_config["handlers"]["mail"]["toaddrs"] = error_email

    if log_level:
        base_config["root"]["level"] = log_level
        base_config["loggers"]["crmprtd"]["level"] = log_level

    logging.config.dictConfig(base_config)


def subset_dict(a_dict, keys_wanted):
    return {key: a_dict[key] for key in keys_wanted if key in a_dict}
