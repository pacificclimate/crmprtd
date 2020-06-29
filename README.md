# crmprtd

![Python CI](https://github.com/pacificclimate/crmprtd/workflows/Python%20CI/badge.svg?branch=master)
![Pypi Publishing](https://github.com/pacificclimate/crmprtd/workflows/Pypi%20Publishing/badge.svg?branch=master)

Utility to download near real time weather data and insert it into PCIC's database

## Installation

For production usage, install the latest tagged release from PCIC's PyPI server.

```bash
pip install -i https://pypi.pacificclimate.org/simple crmprtd
# or with JSON logging functionality
pip install -i https://pypi.pacificclimate.org/simple crmprtd[jsonlogger]
```

Or for development, clone the repo and install it from your local source tree.

```bash
git clone git@github.com:pacificclimate/crmprtd
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.pacificclimate.org/simple
pip install .
```

## Usage

The most common usage pattern for the `crmprtd` is to configure a number of scripts to run on an hourly or daily basis.

Some of the data sources require authentication. For most scripts, credentials can be provided as command line arguments, or more preferrably, entries in a yaml config file. A sample version of this file can be see [here](https://github.com/pacificclimate/crmprtd/blob/master/auth.yaml). This is then sources by passing the file location with the `--auth` argument and the key with the `--auth_key` argument.

Each network has a `download_[network_name]` script which will download data.  The standard output stream of this script can be redirected into a file or piped into `crmprtd_process`.  `crmprtd_process` will take the data and run it through a series of formatting changes and checks before inserting the data into the database.

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
download_bc_forestry > cache_filename
crmprtd_process -N bc_forestry < cache_filename
# Or
download_bc_forestry | crmprtd_process -N bc_forestry
# Or
download_bc_forestry | tee cache_filename | crmprtd_process -N bc_forestry
```

More generally:

```bash
download_[network_name] > cache_filename
crmprtd_process -N [network_name] < cache_filename
# Or
download_[network_name] | crmprtd_process -N [network_name]
# Or
download_[network_name] | tee cache_filename | crmprtd_process -N [network_name]
```

### Logging

One thing to be aware of when using pipes and stdout is that you need to ensure that no logging or debugging output from the download script goes to standard out. The default console logger sends logging output to the standard error stream. However, this is configurable, so the user must take care to *not* configure the logging output to go to standard out, lest it get mixed up with the data output stream.

## Testing

Database tests use the `testing.postgresql` database fixture. This requires `postgresql` server in your `PATH` with the `postgis` extension. This should be as simple as:

```bash
apt-get install postgresql postgis
pip install -r test_requirements.txt
py.test -v tests
```

## Releasing

1. Increment `__version__` in `setup.py`
2. Summarize release changes in `NEWS.md`
3. Commit these changes, then tag the release
```bash
git add setup.py NEWS.md
git commit -m"Bump to version x.x.x"
git tag -a -m"x.x.x" x.x.x
git push --follow-tags
```
4. Actions will build and release the package
