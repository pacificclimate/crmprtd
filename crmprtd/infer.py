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
from crmprtd.align import get_variable


def create_variable(sesh, network_name, variable_name, unit):
    network = sesh.query(Network).filter(Network.name == network_name)

    return sesh.add(
        Variable(
            network=network,
            name=variable_name,
            unit=unit
        )
    )

def infer(sesh, obs_tuples, diagnostic=False):

    vars_to_create = {}
    for obs in obs_tuples:
        variable = get_variable(sesh, obs.network_name, obs.variable_name)

        if not variable:
            vars_to_create.add((obs.network_name, obs.variable_name, obs.unit))

    vars_to_create = [create_variable(sesh, *attrs) for attrs in vars_to_create]

    print(vars_to_create)
