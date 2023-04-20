# Installation: System-level dependencies

For both production and development installation, you must have these
system-level dependencies installed.

We assume you have a supported Python 3 installed on your system.

Certain system packages must be installed in order to install this Python
application:
- PostgreSQL: Typical installation: `sudo apt-get install postgresql-14`,
  which is the current default on our workstations.
- PostGIS: Typical installation: `sudo apt-get install postgresql-14-postgis-3`.
- `libpq-dev`: Permits installation of required Python package `psycopg2`.
  Typical installation: `sudo apt-get install libpq-dev`.

Note: The [Python CI](.github/workflows/python-ci.yml) script purges
PostgreSQL 14 and installs PostgreSQL 12 instead. It can still be used as
a guide for installation in a general way. 

