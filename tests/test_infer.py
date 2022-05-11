from datetime import datetime

import pytest

from crmprtd.infer import infer
from crmprtd import Row
from pycds import Variable, Network


@pytest.mark.parametrize(("diag", "count"), ((True, 0), (False, 2)))
def test_diagnostic(crmp_session, diag, count):
    dt = datetime.now()
    rows = (
        (dt, 0, "test_var_a", "degrees", "MoTIe", "noname", 40, -120),
        (dt, 0, "test_var_a", "degrees", "MoTIe", "noname", 40, -120),
        (dt, 0, "test_var_b", "mm", "MoTIe", "noname", 40, -120),
    )
    rows = (Row(*x) for x in rows)
    crmp_session.add(Network(name="MoTIe"))
    infer(crmp_session, rows, diag)
    q = crmp_session.query(Variable).filter(Variable.name.like("test_var%"))
    assert q.count() == count
