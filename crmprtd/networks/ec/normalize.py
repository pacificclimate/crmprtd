import logging

from importlib.resources import files
from crmprtd import Row
from crmprtd.swob_ml import (
    normalize as swob_ml_normalize,
    get_substitutions,
    apply_substitutions,
)

log = logging.getLogger(__name__)


def normalize(file_stream):
    variable_substitutions_path = "networks/ec/variable_substitutions.yaml"
    variable_substitutions = get_substitutions(variable_substitutions_path)

    rows = swob_ml_normalize(
        file_stream, "EC_raw", station_id_attr="climate_station_number"
    )

    return apply_substitutions(variable_substitutions, rows)
