"""Downloads partner's weather from Environment and Climate Change Canada.

Environment and Climate Change Canada (ECCC) has a section of its
SWOB-ML feed of XML files dedicated to its provincial partners (mostly
from BC). It posts a series of XML files, one file per station per
hour (further details can be found here:
https://dd.weather.gc.ca/observations/doc/README_SWOB.txt). ECCC
appears to maintain the partner data for only 4 to 6 days.

It is recommended to run this script once per hour and maintain
constant monitoring for outtages and errors as even a short outtage
could result in data loss.

"""

import re
import datetime
import logging
import urllib.parse
from io import BytesIO
from argparse import ArgumentParser

from lxml import html
import requests

from crmprtd.download import https_download, verify_date
from crmprtd import add_logging_args, setup_logging, add_version_arg, get_version

log = logging.getLogger(__name__)


def get_url_list(
    base_url="https://dd.weather.gc.ca/observations/swob-ml/partners/" "bc-env-snow/",
    date=datetime.datetime.now(),
):
    """Recursively search an HTML directory tree and yield a set of
    swob.xml URLs that match the given date and hour
    """
    seen = {base_url}
    queue = [base_url]
    sesh = requests.Session()

    while queue:
        # pop the first item off the queue and download
        base_url = queue.pop(0)
        # search for URLs

        log.debug("Downloading {}".format(base_url))
        page = sesh.get(base_url)

        if page.status_code != 200:
            continue
        tree = html.fromstring(page.content)
        urls = tree.xpath("//a/@href")
        # Skip URLs that point to the same page (path is empty)
        urls = [
            urllib.parse.urljoin(base_url, url)
            for url in urls
            if urllib.parse.urlparse(url).path
        ]
        # Skip URLs that are for a different day of interest
        urls = [url for url in urls if match_date(url, date)]
        # Skip URLs that move up the directory tree
        urls = [url for url in urls if url.startswith(base_url)]

        # either return them or add to the queue
        for url in urls:
            if match_swob_xml_url(url, date):
                yield url
            elif url not in seen and not url.endswith("xml"):
                queue.append(url)
            seen.add(url)


def match_swob_xml_url(url, date):
    """Match something like this: 2019-10-18-1600-bc-env-asw-1a02p-AUTO-swob.xml
    or this from DFO: 20220525T0230Z_DFO-CCG_SWOB_1060901.xml
    Returns an re.match object on success, None on failure
    """
    datep_standard = date.strftime("%Y-%m-%d-%H")
    datep_dfo = date.strftime("%Y%m%dT%H30Z")
    search_pattern = re.compile(
        rf"({datep_standard}|{datep_dfo}).*swob.*\.xml", re.IGNORECASE
    )
    return search_pattern.search(url)


def match_date(url, date):
    """Return False if there is a date in the URL but it's not the right date
    Otherwise return True
    """
    has_a_date = re.compile(r"[0-9]{8}")
    has_this_date = re.compile(date.strftime("%Y%m%d"))
    return bool(has_a_date.search(url)) == bool(has_this_date.search(url))


def download(base_url, date):
    urls = get_url_list(base_url, date)
    for url in urls:
        https_download(url, log=log)


def split_multi_xml_stream(stream):
    string = stream.read()
    matches = re.split(rb"(<\?xml.*?\?>)", string)
    matches = matches[1:]
    for _ in range(len(matches) // 2):
        rv = BytesIO(matches.pop(0) + matches.pop(0))
        yield rv


def main(partner):
    """Main download function to use for download scripts for the EC_SWOB
    provincial partners (e.g. bc-env-snow, bc-env-aq, bc-forestry and
    bc-tran).

    Args:
        partner (str): The partner abbreviation found in the SWOB URL
        (e.g. bc-tran)

    Returns:
        No return value. Produces side-effect of sending downloaded
        XML files to STDOUT

    """
    desc = globals()["__doc__"]
    parser = ArgumentParser(description=desc)
    add_version_arg(parser)
    add_logging_args(parser)
    parser.add_argument(
        "-d",
        "--date",
        help=(
            "Alternate date to use for downloading "
            "(interpreted with dateutil.parser.parse)."
            "Defaults to now."
        ),
    )
    args = parser.parse_args()

    if args.version:
        print(get_version())
        return

    setup_logging(
        args.log_conf,
        args.log_filename,
        args.error_email,
        args.log_level,
        "crmprtd.{}".format(partner),
    )

    if not args.date:
        dl_date = datetime.datetime.now()
    else:
        dl_date = verify_date(args.date, datetime.datetime.now(), "date")

    download(
        "https://dd.weather.gc.ca/observations/swob-ml/partners/{}/".format(partner),
        dl_date,
    )


if __name__ == "__main__":
    main("bc-env-snow")
