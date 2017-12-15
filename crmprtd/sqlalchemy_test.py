from sqlalchemy import MetaData
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint


Base = declarative_base(metadata=MetaData(schema='simple'))


class Item(Base):
    __tablename__ = 'meta_network'

    # Columns
    item_id = Column(Integer, primary_key=True)
    name = Column(String)

    # Constraints
    __table_args__ = (
        UniqueConstraint('name', name='item_name_unique'),
    )
