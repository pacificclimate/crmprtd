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
of tuples (time, val, variable name, unit, network name, station id, lat,
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

import io
import time
from collections import namedtuple


Row = namedtuple('Row', "time val variable_name unit network_name station_id \
                         lat lon")


class Timer(object):
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.run_time = self.end - self.start


def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
    """
    Lets you use an iterable (e.g. a generator) that yields
    bytestrings as a read-only input stream.

    The stream implements Python 3's newer I/O API (available in
    Python 2's io module).  For efficiency, the stream is buffered.

    From: goo.gl/Yxm5vz

    """
    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None

        def readable(self):
            return True

        def readinto(self, b):
            try:
                length = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:length], chunk[length:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0    # indicate EOF
    return io.BufferedReader(IterStream(), buffer_size=buffer_size)
