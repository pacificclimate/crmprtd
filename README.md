# crmprtd

[![Build Status](https://travis-ci.org/pacificclimate/crmprtd.svg?branch=master)](https://travis-ci.org/pacificclimate/crmprtd)
[![Code Health](https://landscape.io/github/pacificclimate/crmprtd/master/landscape.svg?style=flat)](https://landscape.io/github/pacificclimate/crmprtd/master)

Utility to download near real time weather data and insert it into PCIC's database

## Installation

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt -i http://tools.pacificclimate.org/pypiserver/ --trusted-host tools.pacificclimate.org
pip install .
```

## Usage

The most common usage pattern for the `crmprtd` is to configure a number of scripts to run on an hourly or daily basis.

Many of the data sources require authentication. For most scripts, credentials can be provided as command line arguments, or more preferrably, entries in a yaml config file. A sample version of this file can be see [here](https://github.com/pacificclimate/crmprtd/blob/master/auth.yaml). This is then sources by passing the file location with the `--auth` argument and the key with the `--auth_key` argument.

Each network has a `[network_name]/download.py` script which will download data.  The output of this script can be piped into a file or into `process.py`.  `process.py` will take the data and run it through a series of formatting changes and checks before inserting the data into the database.

### FLNRO-WMB

`wmb/download.py > filename`
or
`wmb/download.py | process.py`
or
`wmb/download.py | tee filename | process.py`

### EC

`ec/download.py > filename`
or
`ec/download.py | process.py`
or
`ec/download.py | tee filename | process.py`

### MoTIe

`moti/download.py > filename`
or
`moti/download.py | process.py`
or
`moti/download.py | tee filename | process.py`

### ENV-AQN

`wamr/download.py > filename`
or
`wamr/download.py | process.py`
or
`wamr/download.py | tee filename | process.py`


## Testing

Database tests use the `testing.postgresql` database fixture. This requires `postgresql` server in your `PATH` with the `postgis` extension. This should be as simple as:

```bash
apt-get install postgresql postgis
pip install -r test_requirements.txt
py.test -v tests
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
1. Build and release the new package
  - `python setup.py sdist`, then copy the `dist/<package_name>.tar.gz` to the pypiserver, OR
  - `python setup.py sdist upload -r <server>` if you have that set up in your `.pypirc` file
