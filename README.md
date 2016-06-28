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

### FLNRO-WMB

`hourly_wmb.py`

### EC

`real_time_ec.py`

### MoTIe

`moti_hourly.py`


## Testing

Database tests use the `testing.postgresql` database fixture. This requires `postgresql` server in your `PATH` with the `postgis` extension. This should be as simple as:

```bash
apt-get install postgresql postgis
pip install -r test_requirements.txt
py.test -v tests
```
