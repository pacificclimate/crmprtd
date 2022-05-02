"""infer.py

The infer module is an optional phase of the crmprtd pipeline. This
phase takes a sequence of Obs tuples and reports on what database
metadata modifications would need to be made in aggreate to support
the set of observations. This could include the creation of new
variables, the creation of new stations and/or history entries.

A common use case for this module would be when bringing a new network
online, one needs to create database entries for variables to be
tracked in this network. This can't/shouldn't necessarily be done in a
completely automatically for a couple of reasons:

1. Many variables reported by a station are only necessary for
   operational purposes and not for necessarily for climate monitoring
   (e.g. sensor battery voltage). We want to pick which variables to
   track and which to not.

2. Standard data feeds don't typically contain enough metadata to
   automatically fill out the details for a variable. For example,
   they often don't contain anything that could be used to fill out
   the "cell_method" value (which is important for climatological
   analysis), long form descriptions, or other aliases
   (e.g. display_name).

"""

import logging

# local
from pycds import Obs, History, Network, Variable, Station
from crmprtd.align import get_variable, get_history


log = logging.getLogger("crmprtd")


def create_variable(sesh, network_name, variable_name, unit):
    network = sesh.query(Network).filter(Network.name == network_name).one()

    return Variable(network=network, name=variable_name, unit=unit)


def infer(sesh, obs_tuples, diagnostic=False):

    # Use a set to filter down to unique tuples
    vars_to_create = {
        (obs.network_name, obs.variable_name, obs.unit) for obs in obs_tuples
    }
    vars_to_create = [
        create_variable(sesh, network_name, var_name, unit)
        for network_name, var_name, unit in vars_to_create
        if not get_variable(sesh, network_name, var_name)
    ]

    sesh.add_all(vars_to_create)
    for var in vars_to_create:
        log.info(
            f"INSERT INTO meta_vars (network_id, net_var_name, unit) VALUES ({var.network.id}, '{var.name}', '{var.unit}')"
        )

    # Use a set to filter down to unique tuples
    hists_to_create = {
        (obs.network_name, obs.station_id, obs.lat, obs.lon) for obs in obs_tuples
    }
    # The poorly named "get_history" function also does inserts as needed
    hxs = [get_history(sesh, *tup, diagnostic) for tup in hists_to_create]
