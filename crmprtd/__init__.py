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
this phase is simply a file stream and the output is simply a stream
of tuples (time, val, variable name, network name, station id, lat,
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

import time
from functools import wraps

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry
