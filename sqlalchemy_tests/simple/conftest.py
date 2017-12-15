import pytest

import crmprtd.sqlalchemy_test
from sqlalchemy.schema import CreateSchema


@pytest.fixture(scope='function')
def create_test_database():
    def create(engine):
        engine.execute(CreateSchema('simple'))
        crmprtd.sqlalchemy_test.Base.metadata.create_all(bind=engine)
    yield create
