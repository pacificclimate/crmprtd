import pytz
from pint import UnitRegistry


tz = pytz.timezone('Canada/Pacific')
ureg = UnitRegistry()
Q_ = ureg.Quantity
for def_ in (
        "degreeC = degC; offset: 273.15",
        "degreeF = 5 / 9 * kelvin; offset: 255.372222",
        "degreeK = degK; offset: 0"
):
    ureg.define(def_)
