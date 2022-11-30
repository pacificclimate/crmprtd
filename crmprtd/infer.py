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
from crmprtd.align import get_variable, find_or_create_matching_history_and_station


log = logging.getLogger("crmprtd")


def create_variable(
    sesh,
    network_name,
    variable_name,
    unit,
    standard_name=None,
    display_name=None,
    cell_method="undefined",
):
    network = sesh.query(Network).filter(Network.name == network_name).one()

    return Variable(
        network=network,
        name=variable_name,
        standard_name=standard_name or variable_name,
        display_name=display_name or variable_name,
        cell_method=cell_method,
        unit=unit,
    )


def infer(sesh, obs_tuples, diagnostic=False):
    """
    Infer the variables, stations, and histories required by the data.

    This means:
    1. Construct required variables. Add them to database if and only if not in
        diagnostic mode.
    2. Find or create matching history and station records. Always, regardless of
        diagnostic mode.

    :param sesh: SQLAlchemy db session
    :param obs_tuples: Data representing observations to be inserted.
    :param diagnostic: Boolean. In diagnostic mode?
    :return: None
    """

    # Reduce observations to unique set of tuples describing required variables
    vars_to_create = {
        (obs.network_name, obs.variable_name, obs.unit) for obs in obs_tuples
    }

    # Construct required variables. Add them to database if and only if not in
    # diagnostic mode.
    with sesh.begin_nested() as nested:
        vars_to_create = [
            create_variable(sesh, network_name, var_name, unit)
            for network_name, var_name, unit in vars_to_create
            if not get_variable(sesh, network_name, var_name)
        ]

        for var in vars_to_create:
            log.info(
                f"INSERT INTO meta_vars (network_id, net_var_name, unit) "
                f"VALUES ({var.network.id}, '{var.name}', '{var.unit}')"
            )

        if diagnostic:
            nested.rollback()
        else:
            sesh.add_all(vars_to_create)
            nested.commit()

    # Reduce observations to unique set of tuples describing required histories
    # and stations.
    hists_to_create = {
        (obs.network_name, obs.station_id, obs.lat, obs.lon) for obs in obs_tuples
    }

    # Find or create matching histories and stations.
    # TODO: Why is this variable unused? Was it meant to be returned?
    hxs = [
        find_or_create_matching_history_and_station(sesh, *tup, diagnostic)
        for tup in hists_to_create
    ]
