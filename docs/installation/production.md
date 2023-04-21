# Installation for production usage

For production usage, install the latest tagged release from PCIC's PyPI server.

It is best practice to install in a virtual environment. Python version >= 3.8
is now required in the environment in which this package is installed.

Some of our servers do not by default provide Python >= 3.8. If the server
includes the module facility (which `crmprtd.pcic` fortunately does), then
you can obtain a suitable Python environment by loading the appropriate module.
For example:

```bash
module load python/3.8.6
```

Create the virtual environment:

```bash
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ pip install -U pip
```

Then install (with virtual environment still activated):

```bash
(venv) $ pip install -i https://pypi.pacificclimate.org/simple crmprtd
# or with JSON logging functionality
(venv) $ pip install -i https://pypi.pacificclimate.org/simple crmprtd[jsonlogger]
```
