"""infer.py

The infer module is an optional phase of the crmprtd pipeline. This
phase takes a sequence of Obs tuples and reports on what database
metadata modifications would need to be made in aggregate to support
the set of observations. This could include the creation of new
variables, stations and/or history entries.

A common use case for this module would be when bringing a new network
online, one needs to create database entries for variables to be
tracked in this network. This can't/shouldn't necessarily be done in a
completely automatically for several reasons:

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

3. As of version 4.0.0 of PyCDS, several columns in the variables table
   are not nullable and values cannot be derived for them (see point above).
   Therefore it is no longer possible to insert variables with null values
   for these columns. An attempt to insert such variables now raises an exception.
"""

import logging

# local
from pycds import Network, Variable
from crmprtd.align import get_variable, find_or_create_matching_history_and_station
from crmprtd.insert import sanitize_connection

log = logging.getLogger(__name__)


def create_variable(
    sesh,
    network_name,
    variable_name,
    unit,
    standard_name=None,
    display_name=None,
    cell_method=None,
):
    network = sesh.query(Network).filter(Network.name == network_name).one()

    return Variable(
        network=network,
        name=variable_name,
        standard_name=standard_name,
        display_name=display_name,
        cell_method=cell_method,
        unit=unit,
    )


def infer(sesh, rows, diagnostic=False):
    """
    Infer the variables, stations, and histories required by the data.

    This means:
    1. Construct required variables. Add them to database if and only if not in
        diagnostic mode.
    2. Find or create matching history and station records. Always, regardless of
        diagnostic mode.

    :param sesh: SQLAlchemy db session
    :param rows: Collection of Rows representing observations to be inserted.
    :param diagnostic: Boolean. In diagnostic mode?
    :return: None
    """

    # Reduce observations to unique set of tuples describing required histories
    # and stations.
    hists_to_create = {
        (row.network_name, row.station_id, row.lat, row.lon) for row in rows
    }

    # Find or create matching histories and stations.
    # This operation should be done before processing variables, because, in
    # not-diagnostic mode, the latter can raise an exception which would prevent any
    # further work.
    # TODO: Why is this variable unused? Was it meant to be logged or returned?
    hxs = [
        find_or_create_matching_history_and_station(sesh, *tup, diagnostic=diagnostic)
        for tup in hists_to_create
    ]

    # Reduce observations to unique set of tuples describing required variables
    vars_to_create = {(row.network_name, row.variable_name, row.unit) for row in rows}

    # Construct required variables. They are never committed to the database.
    with sesh.begin_nested() as nested:
        variables = [
            create_variable(
                sesh,
                network_name,
                var_name,
                unit,
                standard_name="requires_human_intervention",
                display_name="requires_human_intervention",
                cell_method="requires_human_intervention",
            )
            for network_name, var_name, unit in vars_to_create
            if not get_variable(sesh, network_name, var_name)
        ]

        for var in variables:
            log.info(
                f"INSERT INTO meta_vars (network_id, net_var_name, unit) "
                f"VALUES ({var.network.id}, '{var.name}', '{var.unit}')",
                extra={"database": sanitize_connection(sesh)},
            )

        if diagnostic:
            nested.rollback()
        elif len(variables) > 0:
            raise ValueError(
                f"{len(variables)} Variables need to be inserted (see log). "
                f"This is not possible without human intervention.",
            )
