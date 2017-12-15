import pytest

import crmprtd.sqlalchemy_test.simple
from sqlalchemy.schema import CreateSchema


@pytest.fixture(scope='function')
def create_test_database():
    def create(engine):
        engine.execute(CreateSchema('simple'))
        crmprtd.sqlalchemy_test.simple.Base.metadata.create_all(bind=engine)
    yield create
