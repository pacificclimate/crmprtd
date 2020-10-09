import pytz
from pint import UnitRegistry


tz = pytz.timezone("Canada/Pacific")
ureg = UnitRegistry()
Q_ = ureg.Quantity

# These definitions have been added (https://git.io/Je9RB) since the
# latest release of pint (0.9). This can be removed once we incorporate pint's
# next release.
for def_ in (
    "degreeC = degC; offset: 273.15",
    "degreeF = 5 / 9 * kelvin; offset: 255.372222",
    "degreeK = degK; offset: 0",
):
    ureg.define(def_)
