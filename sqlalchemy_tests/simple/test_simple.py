import pytest
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from crmprtd.sqlalchemy_test.simple import SimpleItem


@pytest.mark.parametrize('rollback', [
    False,
    True,
])
@pytest.mark.parametrize('commit', [
    False,
    True,
])
@pytest.mark.parametrize('method', [
    'Add',
    'Merge'
])
@pytest.mark.parametrize('nested', [
    False,
    True,
])
@pytest.mark.parametrize('names_name, names', [
    # ('A', 'test1 test2'.split()),
    # ('B', 'test1 test1'.split()),
    ('C', 'test1 test2 test2 test3'.split()),
])
def test_several_items(
        test_session_factory,
        insert, final_commit, args, add_result,
        names_name, names,
        nested, method, commit, rollback,
):
    keys = args(names_name, nested, method, commit, rollback)
    print('Test params:', ' | '.join('{}: {}'.format(*key) for key in keys))
    print()

    sesh = test_session_factory()
    for name in names:
        item = SimpleItem(name=name)
        insert(sesh, item, 'name', nested=nested, method=method, commit=commit, rollback=rollback)

    final_commit(sesh)
    sesh.close()

    sesh2 = test_session_factory()
    q = sesh2.query(SimpleItem)
    count = q.count()
    add_result(keys, count)
    # assert count == len(set(names))
    sesh2.close()


@pytest.mark.parametrize('names_name, names', [
    # ('A', 'test1 test2'.split()),
    # ('B', 'test1 test1'.split()),
    ('C', 'test1 test2 test2 test3'.split()),
])
def test_sqlalchemy_doc(
        generic_test_sqlalchemy_doc,
        generic_item_count,
        test_session,
        names_name, names,
):
    items = (SimpleItem(name=name) for name in names)
    generic_test_sqlalchemy_doc(test_session, SimpleItem, items)
    assert generic_item_count(SimpleItem) == len(set(names))
