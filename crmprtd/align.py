"""align.py

The align module handles the Align phase of the crmprtd pipeline. This
phase consists of performing database consistency checks required to
insert the incoming data records. Do the stations already exist or do
we need to create them? Do the variables exist or can we create them?
Etc. The input is a stream tuples and the output is a stream of
pycds.Obs objects. This phase is common to all networks.
"""

from pycds import Obs

def align(sesh, obs_tuples):
    for time, val, var_name, network_name, station_name, lat, lon in obs_tuples:
        # Do checks and make station/variable insertions if necessary/possible
        # Create and yield pycds.Obs object
        yield Obs()
