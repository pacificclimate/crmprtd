from datetime import datetime

import pytest

from crmprtd.infer import infer
from crmprtd import Row
from pycds import Variable, Network, Station, History


# Truth table for infer's behaviour:
# Inputs: diagnostic, new stations, new variables
# Outcomes: whether a commit happens or an exception is raised
#
# | diagnostic | new stations | new variables | commit     | raises |
# |------------|--------------|---------------|------------|--------|
# | False      | True         | True          | no         | yes    |
# | False      | False        | True          | no         | yes    |
# | False      | True         | False         | yes        | no     |
# | False      | False        | False         | irrelevant | no     |
# | True       | True         | True          | no         | no     |
# | True       | False        | True          | no         | no     |
# | True       | True         | False         | no         | no     |
# | True       | False        | False         | irrelevant | no     |
#
# "Irrelevant" can be read as "no".


def make_test_rows(
    session,
    network_name="MoTIe",
    stn_count=1,
    stn_id_prefix="test_stn_id",
    var_count=1,
    var_name_prefix="test_var",
    time=datetime.now(),
    val=0,
    unit="degrees",
):
    """
    Return a collection of rows for testing `infer`
    Implements the inputs side of the truth table above.
    All items are associated to the same network.
    """

    session.add(Network(name=network_name))
    station_ids = tuple(f"{stn_id_prefix}_{i}" for i in range(stn_count))
    variable_names = tuple(f"{var_name_prefix}_{i}" for i in range(var_count))
    return tuple(
        Row(time, val, variable_name, unit, network_name, station_id, 40, -120)
        for station_id in station_ids
        for variable_name in variable_names
    )


def commit_raises(diagnostic=False, stn_count=1, var_count=1):
    """
    Implements the outputs side of the behaviour truth table.
    """
    commit = (not diagnostic) and (stn_count > 0)
    raises = (not diagnostic) and (var_count > 0)
    return commit, raises


@pytest.mark.parametrize("diagnostic", (False, True))
@pytest.mark.parametrize("stn_count", (1, 2))
@pytest.mark.parametrize("var_count", (1, 2))
def test_infer(crmp_session, diagnostic, stn_count, var_count):
    network_name = "MoTIe"
    stn_id_prefix = "test_stn_id"
    var_name_prefix = "test_var"

    stn_query = crmp_session.query(Station).filter(
        Station.native_id.like(f"{stn_id_prefix}%")
    )
    var_query = crmp_session.query(Variable).filter(
        Variable.name.like(f"{var_name_prefix}%")
    )

    pre_stn_count = stn_query.count()
    pre_var_count = var_query.count()

    assert pre_stn_count == 0
    assert pre_var_count == 0

    rows = make_test_rows(
        crmp_session,
        network_name=network_name,
        stn_id_prefix=stn_id_prefix,
        stn_count=stn_count,
        var_name_prefix=var_name_prefix,
        var_count=var_count,
    )

    commit, raises = commit_raises(
        diagnostic=diagnostic, stn_count=stn_count, var_count=var_count
    )

    if raises:
        with pytest.raises(ValueError) as exc_info:
            infer(crmp_session, rows, diagnostic)
    else:
        infer(crmp_session, rows, diagnostic)

    post_stn_count = stn_query.count()
    post_var_count = var_query.count()

    assert post_stn_count == (stn_count if commit else 0)
    assert post_var_count == (var_count if commit and not raises else 0)
