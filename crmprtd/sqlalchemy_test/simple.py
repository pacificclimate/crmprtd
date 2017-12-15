from sqlalchemy import MetaData
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref


Base = declarative_base(metadata=MetaData(schema='simple'))


class SimpleItem(Base):
    __tablename__ = 'simple_items'

    # Columns
    item_id = Column(Integer, primary_key=True)
    name = Column(String)

    # Constraints
    __table_args__ = (
        UniqueConstraint('name', name='item_name_unique'),
    )
