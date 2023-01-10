# crmprtd

![Python CI](https://github.com/pacificclimate/crmprtd/workflows/Python%20CI/badge.svg?branch=master)
![Pypi Publishing](https://github.com/pacificclimate/crmprtd/workflows/Pypi%20Publishing/badge.svg?branch=master)

Utility to download near real time weather data and insert it into PCIC's database

## System-level dependencies

We assume you have a supported Python 3 installed on your system.

Certain system packages must be installed in order to install this Python
package:
- PostgreSQL: Typical installation: `sudo apt-get install postgresql-14`, 
which is the current default on our workstations.
- PostGIS: Typical installation: `sudo apt-get install postgresql-14-postgis-3`.
- `libpq-dev`: Permits installation of required Python package `psycopg2`.
  Typical installation: `sudo apt-get install libpq-dev`.

Note: The [Python CI](.github/workflows/python-ci.yml) script purges 
PostgreSQL 14 and installs PostgreSQL 12 instead. It can still be used as 
a guide for installation in a general way. 

## Installation

Note: The scripts installed by this project include both Python programs and
a set of shell scripts used to download and process data from the various
networks. We call these "execution scripts" for lack of a better term, and
their source is in the directory `crmprtd/execution`. They are a recent addition 
to this repo; formerly they were maintained outside source control.

The execution scripts are installed in the installation environment `bin/` 
directory (e.g., `venv/bin/`), like all other project scripts.

### Installation for production

For production usage, install the latest tagged release from PCIC's PyPI server.

```bash
pip install -i https://pypi.pacificclimate.org/simple crmprtd
# or with JSON logging functionality
pip install -i https://pypi.pacificclimate.org/simple crmprtd[jsonlogger]
```

### Installation for development

For development, clone the repo and install it using Pipenv from your 
local source tree. This is similar to how the Python CI environment is set up.

```bash
git clone git@github.com:pacificclimate/crmprtd
pipenv install --dev .
pipenv run pip install -e .
```

After installation, you can 
- Issue `pipenv shell` to enter a shell that always implicitly uses the virtual 
environment just created.
- Issue `pipenv run ...` commands to run a single command in the virtual
environment.

## Usage

The most common usage pattern for package `crmprtd` is to configure a number of scripts to run on an hourly or daily basis.

Some data sources require authentication. For most scripts, credentials can be provided as command line arguments, or, preferably, entries in a yaml config file. A sample version of this file can be seen [here](https://github.com/pacificclimate/crmprtd/blob/master/auth.yaml). The location of the config is passed with the `--auth` argument and the key with the `--auth_key` argument.

### Downloading data

Script `crmprtd_download -N [network_name]` downloads data for the named network.  
The standard output stream of this script can be redirected into a file or piped 
into `crmprtd_process`.  Script `crmprtd_process` read data from the standard input
stream runs it through a series of formatting changes and checks before inserting 
the data into the database.

A list of all available network modules can be found in the online help for `crmprtd_process`:

```bash
(env) james@basalt:~/code/git/crmprtd$ crmprtd_process -h
usage: crmprtd_process [-h] -c CONNECTION_STRING [-D]
                       [--sample_size SAMPLE_SIZE]
                       [-N {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,ec,moti,wamr,wmb}]
                       [-L LOG_CONF] [-l LOG_FILENAME]
                       [-o {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-m ERROR_EMAIL]

optional arguments:
...
  -N {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,ec,moti,wamr,wmb}, --network {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,ec,moti,wamr,wmb}
                        The network from which the data is coming from. The
                        name will be used for a dynamic import of the module's
                        normalization function.
```

### Input/Output Streams

Connecting the I/O of the download scripts to cache files and the processing scripts is as easy as using unix pipes and I/O redirects. For example, fetching the SWOB-ML for the BC Forestry data and processing it, looks like this:

```bash
crmprtd_download -N bc_forestry > cache_filename
crmprtd_process -N bc_forestry < cache_filename
# Or
crmprtd_download -N bc_forestry | crmprtd_process -N bc_forestry
# Or
crmprtd_download -N bc_forestry | tee cache_filename | crmprtd_process -N bc_forestry
```

More generally:

```bash
crmprtd_download -N [network_name] > cache_filename
crmprtd_process -N [network_name] < cache_filename
# Or
crmprtd_download -N [network_name] | crmprtd_process -N [network_name]
# Or
crmprtd_download -N [network_name] | tee cache_filename | crmprtd_process -N [network_name]
```

### Execution scripts

Most execution scripts receive 2 or more arguments, as follows:

| Script              | Arguments                      |
|---------------------|--------------------------------|
| `bch.sh`            | `<tag> <database>`             |
| `crd.sh`            | `<tag> <database>`             |
| `ec.sh`             | `<frequency> <tag> <database>` |
| `hourly_swobml2.sh` | `<tag> <database>`             |
| `metnorth.sh`       | `<tag> <database>`             |
| `moti.sh`           | `<tag> <database>`             |
| `wamr.sh`           | `<tag> <database>`             |
| `wmb.sh`            | `<tag> <database>`             |

Arguments:

- `<tag>`: A short tag that becomes part of the filepaths for cache and log files.
  Usually indicates the target database (but is not the database DSN, which
  is not suitable for forming a filepath). Examples: `crmp`, `metnorth`, `metnorth2`.
- `<database>`: DSN for target database. Example: `postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp`
- `<frequency>`: Frequency of observations; used only in EC downloads.

### Cron usage

Typical usage is to set up a cron job that invokes an execution script at the
appropriate times. An example partial crontab using the above scripts is:

```text
SHELL=/bin/bash

CRMP_BIN=env_3.5.1/bin
CRMP_DB=postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp

METNORTH_BIN=env_3.5.1/bin
METNORTH_DB=postgresql://crmprtd@dbnorth/metnorth

METNORTH2_BIN=env_4.0.0/bin
METNORTH2_DB=postgresql://crmprtd@dbnorth/metnorth2

@hourly                         $CRMP_BIN/hourly_swobml2.sh crmp $CRMP_DB
@weekly                         $CRMP_BIN/wamr.sh crmp $CRMP_DB
40 4 * * *                      $CRMP_BIN/wmb.sh crmp $CRMP_DB
@hourly                         $CRMP_BIN/ec.sh hourly crmp $CRMP_DB
@daily                          $CRMP_BIN/ec.sh daily crmp $CRMP_DB
30 * * * *                      $CRMP_BIN/moti.sh crmp $CRMP_DB
@daily                          $CRMP_BIN/crd.sh crmp $CRMP_DB
@daily                          $CRMP_BIN/bch.sh crmp $CRMP_DB
@hourly                         $METNORTH_BIN/ytnt.sh metnorth $METNORTH_DB
@hourly                         $METNORTH2_BIN/ytnt.sh metnorth2 $METNORTH2_DB
```

Notes:
- Variables defined inside the crontab are used to shorten the script invocations
  and to simpify maintenance.
- The Metnorth processing targets different databases with different tags to
  distinguish the cache and log files produced by each job.

### Logging

One thing to be aware of when using pipes and stdout is that you need to ensure that no logging or debugging output from the download script goes to standard out. The default console logger sends logging output to the standard error stream. However, this is configurable, so the user must take care to *not* configure the logging output to go to standard out, lest it get mixed up with the data output stream.

## Testing

Database tests use the `testing.postgresql` database fixture. This requires `postgresql` server in your `PATH` with the `postgis` extension. This should be as simple as:

```bash
apt-get install postgresql postgis
pip install -r test_requirements.txt
py.test -v tests
```

## Formatting

We use `black` coupled with `pre-commit hooks` to handle our formatting needs. By default `make` will install both of these packages into the virtual environment.

### `black`

To manually install and format with `black`:
```
pipenv shell
black .
```

### `pre-commit`

The `pre-commit hook` will only be triggered if the venv has been activated. If triggered, there will be a warning blocking the commit and the file(s) will automatically be reformatted. From there the files will need to be staged again.

To manually install `pre-commit`:
```
pipenv shell
pre-commit install
```

## Releasing

1. Increment `__version__` in `setup.py`
1. Summarize release changes in `NEWS.md`
1. Commit these changes, then tag the release
```bash
git add setup.py NEWS.md
git commit -m"Bump to version x.x.x"
git tag -a -m"x.x.x" x.x.x
git push --follow-tags
```
1. Our Github Actions [workflow](https://github.com/pacificclimate/crmprtd/blob/i71-action-best-practices/.github/workflows/python-ci.yml) will build and release the package
