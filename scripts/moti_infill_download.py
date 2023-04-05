#!/usr/bin/env python

import os
import logging
import logging.config
from urllib.parse import urlparse, parse_qs
from pkg_resources import resource_stream
from datetime import datetime
from argparse import ArgumentParser

import yaml
import pytz
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pycds import CrmpNetworkGeoserver as CNG
from crmprtd.networks.moti import url_generator


def download(url, auth, out, log):
    # Configure requests to use retry
    s = requests.Session()
    a = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount("https://", a)
    req = s.get(url, auth=auth)

    log.info("Status", extra={"status_code": req.status_code, "url": req.url})
    if req.status_code != 200:
        raise IOError("HTTP {} error for {}".format(req.status_code, req.url))

    with open(out, "wb") as f:
        f.write(req.content)
        log.info("Saved file", extra={"file": out})


def url_to_from(url):
    parsed = parse_qs(urlparse(url).query)
    return (parsed["from"][0].replace("/", "T"), parsed["to"][0].replace("/", "T"))


def main(args):
    # Setup logging
    log_conf = yaml.load(args.log_conf)
    if args.log:
        log_conf["handlers"]["file"]["filename"] = args.log
    else:
        args.log = log_conf["handlers"]["file"]["filename"]
    if args.error_email:
        log_conf["handlers"]["mail"]["toaddrs"] = args.error_email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger("crmprtd.networks.moti")
    if args.log_level:
        log.setLevel(args.log_level)

    # Pull auth from file or command line
    if args.bciduser or args.bcidpass:
        assert args.bciduser and args.bcidpass, (
            "Must provide both a "
            "bciduser and password, or "
            "neither to use auth "
            "file/key method"
        )
        auth = (args.bciduser, args.bcidpass)
    else:
        assert args.auth and args.auth_key, (
            "Must provide both the auth file "
            "and the key to use for this "
            "script (--auth_key)"
        )
        with open(args.auth, "r") as f:
            config = yaml.load(f)
        auth = (config[args.auth_key]["username"], config[args.auth_key]["password"])

    # Figure out timespan desired
    # Times input from command line should be in pacific time
    pacific = pytz.timezone("America/Vancouver")
    start_time = datetime.strptime(args.start_time, "%Y/%m/%d %H:%M:%S")
    start_time = pacific.localize(start_time)
    if args.end_time:
        end_time = datetime.strptime(args.end_time, "%Y/%m/%d %H:%M:%S")
        end_time = pacific.localize(end_time)
    else:
        end_time = datetime.now(pacific)

    if args.station_id:
        for url in url_generator(args.station_id, start_time, end_time):
            to, _from = url_to_from(url)
            outfile = os.path.join(
                args.output_dir,
                "moti-sawr7110_station-{}_{}_{}.xml".format(args.station_id, to, _from),
            )
            try:
                download(url, auth, outfile, log)
            except IOError as e:
                log.exception("Unable to download file")
                continue
    else:
        engine = create_engine(args.connection_string)
        sesh = sessionmaker(bind=engine)()
        q = sesh.query(CNG.native_id).filter(CNG.network_name == "MoTIe")
        for (station_id,) in q.all():
            for url in url_generator(station_id, start_time, end_time):
                to, _from = url_to_from(url)
                outfile = os.path.join(
                    args.output_dir,
                    "moti-sawr7110_station-{}_{}_{}.xml".format(station_id, to, _from),
                )
                try:
                    download(url, auth, outfile, log)
                except IOError as e:
                    log.exception("Unable to download file")
                    continue


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--connection_string",
        required=True,
        help=(
            "PostgreSQL connection string of form:"
            "\n\tdialect+driver://username:password@host:"
            "port/database\n"
            "Examples:"
            "\n\tpostgresql://scott:tiger@localhost/"
            "mydatabase"
            "\n\tpostgresql+psycopg2://scott:tiger@"
            "localhost/mydatabase"
            "\n\tpostgresql+pg8000://scott:tiger@localhost"
            "/mydatabase"
        ),
    )
    parser.add_argument(
        "-y", "--log_conf", default=resource_stream("crmprtd", "/data/logging.yaml")
    )
    parser.add_argument("-l", "--log", dest="log", help="log filename")
    parser.add_argument(
        "--log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=(
            "Set log level: DEBUG, INFO, WARNING, ERROR, "
            "CRITICAL.  Note that debug output by default "
            "goes directly to file"
        ),
    )
    parser.add_argument(
        "-e",
        "--error_email",
        dest="error_email",
        help=(
            "e-mail address to which the program should "
            "report error which require human intervention"
        ),
    )
    parser.add_argument(
        "-S",
        "--start_time",
        required=True,
        help=(
            "Alternate time to use for downloading "
            "(interpreted with "
            "strptime(format='Y/m/d H:M:S') "
            "in Pacific Time"
        ),
    )
    parser.add_argument(
        "-E",
        "--end_time",
        help=(
            "Alternate time to use for downloading "
            "(interpreted with"
            "strptime(format='Y/m/d H:M:S') "
            "in Pacific Time"
        ),
    )
    parser.add_argument(
        "-i", "--station_id", help="Station ID for which to download data"
    )
    parser.add_argument("--auth", help="Yaml file with plaintext usernames/passwords")
    parser.add_argument(
        "--auth_key", help=("Top level key which user/pass are stored in yaml " "file.")
    )
    parser.add_argument(
        "--bciduser", dest="bciduser", help="The BCID username for data requests"
    )
    parser.add_argument(
        "--bcidpass", dest="bcidpass", help="The BCID password for data requests"
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        help="directory in which to put the downloaded file",
    )

    args = parser.parse_args()
    main(args)
