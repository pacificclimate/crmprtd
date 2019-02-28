from io import StringIO

import pytest

from crmprtd.download import extract_auth


@pytest.mark.parametrize(('user', 'password', 'expected'), (
    ('foo', 'bar', {'u': 'foo', 'p': 'bar'}),
    ('foo', None, {'u': 'foo', 'p': ''}),
    (None, 'bar', {'u': '', 'p': 'bar'}),
    (None, None, {'u': 'user_from_file', 'p': 'pw_from_file'})
))
def test_extract_auth(user, password, expected):
    yaml = StringIO('''my_test:
  username: user_from_file
  password: pw_from_file
''')
    assert extract_auth(user, password, yaml, 'my_test') == expected
