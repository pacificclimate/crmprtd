from collections import OrderedDict
import json

import pytest
import testing.postgresql

import sqlalchemy.event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError


# Because the tests commit values, we cannot use scopes bigger than 'function' to establish
# the test database or engine.
#
# If the session yielded by test_session were a nested session, then we could according to documentation
# roll back that session and get a clean database for each test with module- or session-scoped
# database (dsn) and engine fixtures. But nested sessions are under question here, so at least at
# first we have to use function-scoped fixtures.

@pytest.fixture(scope='function')
# @pytest.fixture(scope='session')
def test_dsn():
    with testing.postgresql.Postgresql() as pg:
        dsn = pg.url()
        print('Postgres test dsn:', dsn)
        yield dsn


@pytest.fixture(scope='function')
# @pytest.fixture(scope='session')
def test_engine(test_dsn, create_test_database):
    engine = create_engine(test_dsn)
    create_test_database(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope='function')
# @pytest.fixture(scope='session')
def test_session_factory(test_engine):
    Session = sessionmaker(bind=test_engine)
    yield Session


@pytest.fixture
def test_session(test_session_factory):
    session = test_session_factory()
    yield session
    # session.rollback()
    session.close()


@pytest.fixture(scope='function')
def generic_test_sqlalchemy_doc(test_session_factory):
    def test_sqlalchemy_doc(
            prepared_session,  # session prepared with any necessary adjunct objects for insertion of items
            OrmItem,  # ORM class of items to be inserted
            items,  # iterable of items to be inserted
    ):

        def print_items(tag):
            print_sesh = test_session_factory()
            q = print_sesh.query(OrmItem)
            count = q.count()
            print()
            print(count, 'Items in database: {}'.format(tag))
            for item in q.all():
                print(item)
            print_sesh.close()

        print_items('Before inserts')

        print()
        for item in items:
            try:
                with prepared_session.begin_nested():
                    prepared_session.merge(item)
                print("Inserted {}".format(item))
            except Exception as e:
                print("Skipped {} ({})".format(item, e.__class__.__name__))
            prepared_session.commit()
        prepared_session.close()

        print_items('After inserts')

    yield test_sqlalchemy_doc


@pytest.fixture(scope='function')
def generic_item_count(test_session_factory):
    def item_count(OrmItem):
        sesh2 = test_session_factory()
        q = sesh2.query(OrmItem)
        return q.count()
        sesh2.close()
    yield item_count


@pytest.fixture(scope='module')
def insert():
    def f(sesh, item, item_attr_name, nested=False, method='add', commit=False, rollback=False):

        def do_it():
            {'add': sesh.add, 'merge': sesh.merge}[method.lower()](item)

        try:
            print('Insert', getattr(item, item_attr_name))
            if nested:
                with sesh.begin_nested():
                    do_it()
            else:
                do_it()
            if commit:
                sesh.commit()
        except IntegrityError as e:
            print('>> ', e.__class__.__name__)
            if rollback:
                sesh.rollback()
        except InvalidRequestError as e:
            print('>> ', e.__class__.__name__)
            if rollback:
                sesh.rollback()
        # print('\tInsert end')

    yield f


@pytest.fixture(scope='module')
def final_commit():
    def f(sesh):
        print('Final commit')
        try:
            sesh.commit()
            print('>> success')
        except IntegrityError as e:
            print('>> ', e.__class__.__name__)
        except InvalidRequestError as e:
            print('>> ', e.__class__.__name__)

    yield f



@pytest.fixture(scope='module')
def args():
    def f(names, nested, method, commit, rollback):
        return (
            ('names', names),
            ('nested', nested),
            ('method', method),
            ('commit', commit),
            ('rollback', rollback),
        )

    yield f


@pytest.fixture(scope='module')
def add_result():
    results = OrderedDict()

    def add(args, value):
        d = results
        for arg in args:
            key = '{}:{}'.format(*arg)
            d_prev = d
            d[key] = d.get(key, OrderedDict())
            d = d[key]
        d_prev[key] = value

    yield add

    # print('\nResults:')
    # print(json.dumps(results, indent=2))

    print('\nResults:')
    indent = '\t'
    for names, name_results in results.items():
        print()
        print(indent*0, names)
        for nested, nested_results in name_results.items():
            print(indent*1, nested)
            for method, method_results in nested_results.items():
                print(indent*2, method)
                for i, (commit, commit_results) in enumerate(method_results.items()):
                    if (i == 0):
                        print(indent*3, '\t', '\t'.join(commit_results.keys()))
                    print(indent*3, commit, '\t', '\t'.join(str(rollback_result) for rollback_result in commit_results.values()))