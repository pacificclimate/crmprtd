from datetime import datetime

import pytest
import pytz
import psycopg2
import sqlalchemy.exc

from pycds import Network, Variable, History, Station, Obs
from crmprtd.db import mass_insert_obs


def test_mass_insert_obs(test_session):
    history = test_session.query(History).first()
    variable = history.station.network.variables[0]
    
    x = Obs(history=history, datum=2.5, variable=variable, time=datetime(2017, 8, 6, 1, tzinfo=pytz.utc))
    y = Obs(history=history, datum=2.5, variable=variable, time=datetime(2017, 8, 6, 1, tzinfo=pytz.utc))
    # I'm not sure why this has to be done...
    test_session.expunge(x)
    test_session.expunge(y)

    assert mass_insert_obs(test_session, []) == 0
    assert mass_insert_obs(test_session, [x]) == 1
    assert mass_insert_obs(test_session, [y]) == 0
    

def test_mass_insert_obs_duplicates(test_session):
    sesh = test_session

    # Just pick a randon variable and history entry (doesn't matter which)
    history = sesh.query(History).first()
    variable = history.station.network.variables[0]

    # Create 5 observations that are exactly the same
    # Repeat insertions will fail the unique contraint on history/time/variable
    obs = [Obs(history=history, datum=2.5, variable=variable, time=datetime(2012, 9, 24, 6, tzinfo=pytz.utc)) for _ in range(5)]

    # Let the mass_insert function handle the duplicates
    # Only one should be inserted
    assert mass_insert_obs(sesh, obs) == 1
