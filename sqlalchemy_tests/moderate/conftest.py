import pytest

from crmprtd.sqlalchemy_test.moderate import Base, History, Obs
from sqlalchemy.schema import CreateSchema


@pytest.fixture(scope='function')
def create_test_database():
    def create(engine):
        engine.execute(CreateSchema('moderate'))
        Base.metadata.create_all(bind=engine)
    yield create


@pytest.fixture
def history():
    return History()
