# Standard module
import os, sys
import logging, logging.config
from datetime import datetime, timedelta

# Installed libraries
import requests
import yaml

# Local
from crmprtd.ec import makeurl, extract_fname_from_url
from crmprtd.ec.normalize import prepare


def logging_setup(log_conf, log, error_email, log_level):
    with open(log_conf, 'rb') as f:
        log_conf = yaml.load(f)
    if log:
        log_conf['handlers']['file']['filename'] = log
    else:
        log = log_conf['handlers']['file']['filename']
    if error_email:
        log_conf['handlers']['mail']['toaddrs'] = error_email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger('crmprtd.ec')
    if log_level:
        log.setLevel(log_level)

    return log


def download(log, frequency, province, language, time, cache_dir):
    # Configure requests to use retry
    s = requests.Session()
    a = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount('https://', a)

    # Construct and download the xml
    url = makeurl(frequency, province, language, time)
    fname = os.path.join(cache_dir, extract_fname_from_url(url))

    log.info("Downloading {0}".format(url))
    req = s.get(url)
    if req.status_code != 200:
        raise IOError("HTTP {} error for {}".format(req.status_code, req.url))

    log.info("Saving data to {0}".format(fname))
    with open(fname, 'wb') as f:
        f.write(req.content)

    return fname


def run(args):
    # Setup logging
    log = logging_setup(args.log_conf, args.log, args.error_email, args.log_level)
    log.info('Starting EC rtd')

    try:
        if args.filename:
            log.debug("Opening local xml file {0} for reading".format(args.filename))
            fname = args.filename
            xml_file = open(args.filename, 'r')  # Do not catch exception here
            log.debug("File opened sucessfully")

            ec_normalize(args, log, xml_file)
        else:
            # Determine time parameter
            if args.time:
                args.time = datetime.strptime(args.time, '%Y/%m/%d %H:%M:%S')
                log.info("Starting manual run using timestamp {0}".format(args.time))
            else:
                deltat = timedelta(1/24.) if args.frequency == 'hourly' else timedelta(1) # go back a day
                args.time = datetime.utcnow() - deltat
                log.info("Starting automatic run using timestamp {0}".format(args.time))

            fname = download(log, args.frequency, args.province, args.language, args.time, args.cache_dir)
            prepare(args, log, fname)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)
