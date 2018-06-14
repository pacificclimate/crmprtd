#!/usr/bin/env python
#
# One time use script for loading station metadata for WAMR from an
# Excel spreadsheet. Takes one argument on the command line: the
# input file. Hack the engine (line 31) if you actually need to use
# this again


import sys
from collections import namedtuple

import xlrd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pycds import Network, Station, History

if __name__ == '__main__':
    stn_file = sys.argv[1]
    print("Loading stations from file {}".format(stn_file))
    wb = xlrd.open_workbook(stn_file)
    sheet = wb.sheets()[0]
    rows = sheet.get_rows()

    # Consume the header
    header = next(rows)
    names = [foo.value for foo in header]

    WAMRStation = namedtuple('WAMRStation', names)

    engine = create_engine('postgresql://hiebert@monsoon.pcic/crmp')
    sesh = sessionmaker(bind=engine)()
    env_aqn = sesh.query(Network).filter(Network.name == 'ENV-AQN').first()
    print("Found the network", env_aqn)

    for row in rows:
        stn = WAMRStation(*[x.value for x in row])
        print(stn)
        # Do we have this station already?
        q = sesh.query(Station).filter(Station.network == env_aqn).filter(
            Station.native_id == stn.EMS_ID)
        if q.count():
            print(("We already have station {}/{} in the "
                   "database").format(stn.EMS_ID, stn.STATION))
            # Does the location/elevation agree?
            estn = q.first()
            if len(estn.histories) == 0:
                print("No history entries for station. We'll insert.")
                hist = History(station=estn, lat=stn.LAT, lon=stn.LONG,
                               elevation=stn.ELEVATION, province='BC',
                               freq='1-hourly', station_name=stn.STATION)
                sesh.add(hist)
            if len(estn.histories) == 1:
                hist = estn.histories[0]
                tol = .001
                if(abs(float(hist.lon) - stn.LONG) < tol and
                   abs(float(hist.lat) - stn.LAT) < tol and
                   hist.elevation == stn.ELEVATION):
                    print("Good, everything agrees")
                else:
                    print("Our single history entry for this station "
                          "disagrees with the input and we need human "
                          "disambiguation")
                    print(("Us: {} {} {}, Them: {} {} {}. Pick one "
                           "(type 'l' or 'r')").format(hist.lon,
                                                       hist.lat,
                                                       hist.elevation,
                                                       stn.LONG,
                                                       stn.LAT,
                                                       stn.ELEVATION))
                    choice = input()
                    if choice == 'l':
                        print("Keeping status quo")
                    elif choice == 'r':
                        hist.lon = stn.LONG
                        hist.lat = stn.LAT
                        hist.elevation = stn.ELEVATION
                        hist.the_geom = 'SRID=4326;POINT({} {})'.format(
                            stn.LONG, stn.LAT)
                    else:
                        print("OK, I'll skip it")
            else:
                print("Multiple history entries for this station. "
                      "No clue what to do.")
        else:
            print(("Station {}/{} is *not* in the database. "
                   "We'll insert.").format(stn.EMS_ID, stn.STATION))
            estn = Station(native_id=stn.EMS_ID, network=env_aqn)
            hist = History(station=estn, lat=stn.LAT, lon=stn.LONG,
                           the_geom='SRID=4326;POINT({} {})'.format(
                               stn.LONG, stn.LAT),
                           elevation=stn.ELEVATION, province='BC',
                           freq='1-hourly', station_name=stn.STATION)

            sesh.add_all([estn, hist])
        print("Success\n")
        sesh.commit()
