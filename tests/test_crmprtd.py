import pytest

from crmprtd import subset_dict

@pytest.mark.parametrize(('a_dict', 'keys', 'expected'), (
    ({'a': 'b', 'c': 'd', 'e': 'f'}, ['a', 'e'], {'a': 'b', 'e': 'f'}),
    ({'a': 'b'}, ['a'], {'a': 'b'}),
    ({'a': 'b'}, ['c'], {}),
))
def test_subset_dict(a_dict, keys, expected):
    assert subset_dict(a_dict, keys) == expected
