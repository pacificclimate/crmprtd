from sqlalchemy import MetaData
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint


Base = declarative_base(metadata=MetaData(schema='moderate'))


# Simplified case modelled after PyCDS, no 'relationship' components declared

class History(Base):
    __tablename__ = 'meta_history'
    id = Column('history_id', Integer, primary_key=True)

    def __repr__(self):
        return "<History(id={})>".format(self.id)


class Obs(Base):
    __tablename__ = 'obs_raw'
    id = Column('obs_raw_id', BigInteger, primary_key=True)
    time = Column('obs_time', DateTime)
    history_id = Column(Integer, ForeignKey('meta_history.history_id'))

    # Constraints
    __table_args__ = (
        UniqueConstraint('obs_time', 'history_id',
                         name='time_place_unique'),
    )

    def __repr__(self):
        return "<Obs(time={}, history_id={})>".format(self.time, self.history_id)
