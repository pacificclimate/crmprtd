import re
import datetime
import logging
import urllib.parse

from lxml import html
import requests


log = logging.getLogger(__name__)


def get_url_list(
    base_url='https://dd.weather.gc.ca/observations/swob-ml/partners/'
             'bc-env-snow/',
    date=datetime.datetime.now()
):
    '''Recursively search an HTML directory tree and yield a set of
       swob.xml URLs that match the given date and hour
    '''
    seen = {base_url}
    queue = [base_url]
    sesh = requests.Session()

    # Match something like this: 2019-10-18-1600-bc-env-asw-1a02p-AUTO-swob.xml
    search_pattern = re.compile(r'{}.*swob\.xml'.
                                format(date.strftime('%Y-%m-%d-%H')))

    while queue:
        # pop the first item off the queue and download
        base_url = queue.pop(0)
        # search for URLs

        log.debug("Downloading {}".format(base_url))
        page = sesh.get(base_url)

        if page.status_code != 200:
            continue
        tree = html.fromstring(page.content)
        urls = tree.xpath('//a/@href')
        # Skip URLs that point to the same page (path is empty)
        urls = [urllib.parse.urljoin(base_url, url) for url in urls if
                urllib.parse.urlparse(url).path]
        # Skip URLs that are for a different day of interest
        urls = [url for url in urls if match_date(url, date)]
        # Skip URLs that move up the directory tree
        urls = [url for url in urls if url.startswith(base_url)]

        # either return them or add to the queue
        for url in urls:
            if search_pattern.search(url):
                yield url
            elif url not in seen and not url.endswith('xml'):
                queue.append(url)
            seen.add(url)


def match_date(url, date):
    '''Return False if there is a date in the URL but it's not the right date
       Otherwise return True
    '''
    has_a_date = re.compile(r'[0-9]{8}')
    has_this_date = re.compile(date.strftime('%Y%m%d'))
    return bool(has_a_date.search(url)) == bool(has_this_date.search(url))


def split_multi_xml_stream(stream):
    string = ''.join(stream)
    matches = re.split(r'(<\?xml.*?\?>)', string)
    matches = matches[1:]
    for _ in range(len(matches) // 2):
        rv = matches.pop(0) + matches.pop(0)
        yield rv
