from collections import Iterable

import pytest

from .swob_data import multi_xml_download
from crmprtd.bc_env_aq.normalize import normalize as norm_aq
from crmprtd.bc_env_snow.normalize import normalize as norm_snow
from crmprtd.bc_forestry.normalize import normalize as norm_forest
from crmprtd.bc_tran.normalize import normalize as norm_tran


@pytest.mark.parametrize('function', [
    norm_aq,
    norm_snow,
    norm_forest,
    norm_tran
])
def test_normalize(function):
    iterator = function(multi_xml_download)
    assert isinstance(iterator, Iterable)
    for x in iterator:
        assert True
