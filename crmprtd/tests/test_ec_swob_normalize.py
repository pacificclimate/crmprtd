from io import BytesIO
import re
import logging
from collections.abc import Iterable
from importlib import import_module

import pytest

from crmprtd import SWOB_PARTNERS
from .swob_data import multi_xml_download, MSNG_values_xml

normalize_mods = (
    import_module(f"crmprtd.networks.{partner}.normalize") for partner in SWOB_PARTNERS
)
from crmprtd.networks.bc_tran.normalize import normalize as norm_tran


@pytest.mark.parametrize("function", (x.normalize for x in normalize_mods))
def test_normalize(function):
    iterator = function(BytesIO(multi_xml_download))
    assert isinstance(iterator, Iterable)
    for x in iterator:
        assert True


def test_normalize_missing_values(caplog):
    # The test data here has 3 missing values that shouldn't generate anything
    # and 1 actual value that should
    iterator = norm_tran(BytesIO(MSNG_values_xml))
    assert isinstance(iterator, Iterable)
    assert next(iterator)
    with (
        pytest.raises(StopIteration),
        caplog.at_level(logging.DEBUG, logger="crmprtd.swob_ml"),
    ):
        next(iterator)
        # There should be 3 DEBUG log messages about skipping a MSNG value
        assert re.search(r"(Ignoring.*){3}", caplog.text)
