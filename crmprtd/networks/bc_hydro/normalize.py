import re
import sys
import logging
from itertools import islice
from time import perf_counter
from contextlib import contextmanager
from importlib.resources import files
import yaml

from dateutil import parser as date_parse
import pytz

from crmprtd import Row
from crmprtd import setup_logging

log = logging.getLogger(__name__)


def normalize(file_stream):
    headers = []

    # All of the BC Hydro data seem to be either comma delimited or a
    # mixture of a tab and other whitespace to make it fixed
    # width. This pattern encapsulates either
    sep_pattern = re.compile("\\s*[\t,]+\\s*")

    # Detect if numbers are convertible
    num_pattern = re.compile(r"-?\d+(\.\d+)?$")

    variable_substitutions_path = "networks/bc_hydro/variable_substitutions.yaml"
    try:
        with (files("crmprtd") / variable_substitutions_path).open("rb") as f:
            variable_substitutions = yaml.safe_load(f)
    except FileNotFoundError:
        log.warning(
            f"Cannot open resource file '{variable_substitutions_path}'. "
            f"Proceeding with normalization, but there's a risk that variable names will not be recognized."
        )
        return

    for line in file_stream:
        line = line.decode("utf-8")

        # Heuristically guess whether each line is one of three types:
        # a) a free form station name
        # b) a heading line containing variable names, or
        # c) a data line
        # This is absolutely not error proof, but in encapsulates
        # everything I've seen in their data.

        #  Detect station headings and ignore. Station codes are in
        #  the data lines as well
        if not sep_pattern.search(line):
            log.debug(f"No separator detected in line: {line}")
            continue

        # Detect header lines
        elif re.search("date", line, re.IGNORECASE):
            # some variable names contain spaces (*eyeroll*)
            headers = [x.replace(" ", "_") for x in sep_pattern.split(line)]

        # Default to data lines
        else:
            if not headers:
                log.error(f"No headers available for data line: '{line}'")
                continue
            values = sep_pattern.split(line)
            stn_id = values[0]
            obs_time = date_parse.parse(values[1])
            if obs_time.tzinfo is None or obs_time.utcoffset(None) is None:
                tz = pytz.timezone("Canada/Pacific")
                obs_time = tz.localize(obs_time).astimezone(pytz.utc)

            for value, varname in islice(zip(values, headers), 2, None):
                if value == "+":  # this is NaN
                    log.debug(f"{varname}: NaN")
                    continue

                elif num_pattern.match(value):
                    value = float(value)

                    if varname in variable_substitutions:
                        varname = variable_substitutions[varname]

                    yield Row(
                        time=obs_time,
                        val=value,
                        variable_name=varname,
                        network_name="BCH",
                        station_id=stn_id,
                        unit=None,
                        lat=None,
                        lon=None,
                    )
                else:
                    log.debug(
                        f"Could not convert value '{value}' to float (it's probably a QC flag)"
                    )


if __name__ == "__main__":  # noqa
    if sys.argv[1] == "stdin":
        stream = sys.stdin.buffer
    else:
        stream = open(sys.argv[1], "rb")

    setup_logging(
        "/home/james/code/git/crmprtd/logging.yaml",
        "./bch_normalize.log",
        "nobody@example.com",
        logging.INFO,
        "crmprtd",
    )
    log.info("Starting")

    @contextmanager
    def catchtime():
        start = perf_counter()
        yield lambda: perf_counter() - start

    with catchtime() as t:
        for i, obs in enumerate(normalize(stream)):
            log.debug(obs)

    log.info(f"Found {i+1} obs in {t():.4f} secs")
