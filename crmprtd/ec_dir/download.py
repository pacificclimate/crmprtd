# Standard module
import os, sys
import logging, logging.config
from datetime import datetime, timedelta

# Installed libraries
import requests
import yaml

# Local
from crmprtd.ec import makeurl, extract_fname_from_url
from crmprtd.ec_dir.normalize import ec_normalize


def ec_download(args):
    # Setup logging
    with open(args.log_conf, 'rb') as f:
        log_conf = yaml.load(f)
    if args.log:
        log_conf['handlers']['file']['filename'] = args.log
    else:
        args.log = log_conf['handlers']['file']['filename']
    if args.error_email:
        log_conf['handlers']['mail']['toaddrs'] = args.error_email
    logging.config.dictConfig(log_conf)
    log = logging.getLogger('crmprtd.ec')
    if args.log_level:
        log.setLevel(args.log_level)

    log.info('Starting EC rtd')

    try:
        if args.filename:
            log.debug("Opening local xml file {0} for reading".format(args.filename))
            fname = args.filename
            xml_file = open(args.filename, 'r') # Do not catch exception here
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

            # Configure requests to use retry
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('https://', a)

            # Construct and download the xml
            url = makeurl(args.frequency, args.province, args.language, args.time)
            fname = os.path.join(args.cache_dir, extract_fname_from_url(url))

            log.info("Downloading {0}".format(url))
            req = s.get(url)
            if req.status_code != 200:
                raise IOError("HTTP {} error for {}".format(req.status_code, req.url))

            log.info("Saving data to {0}".format(fname))
            with open(fname, 'wb') as f:
                f.write(req.content)

            ec_normalize(args, log, fname)

    except IOError:
        log.exception("Unable to download or open xml data")
        sys.exit(1)
