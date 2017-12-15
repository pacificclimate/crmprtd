import pytest

from crmprtd.sqlalchemy_test.moderate_no_rel import Base, History
from sqlalchemy.schema import CreateSchema


@pytest.fixture(scope='function')
def create_test_database():
    def create(engine):
        engine.execute(CreateSchema('moderate_no_rel'))
        Base.metadata.create_all(bind=engine)
    yield create


@pytest.fixture
def history():
    return History()


@pytest.fixture
def test_session_with_history(test_session, history):
    test_session.add(history)
    test_session.commit()
    yield test_session
