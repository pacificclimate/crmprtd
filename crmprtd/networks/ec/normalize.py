import logging
import yaml

from importlib.resources import files
from crmprtd import Row
from crmprtd.swob_ml import normalize as swob_ml_normalize

log = logging.getLogger(__name__)

def normalize(file_stream): 
    
    variable_substitutions_path = "networks/ec/variable_substitutions.yaml"
    try:
        with (files("crmprtd") / variable_substitutions_path).open("rb") as f:
            variable_substitutions = yaml.safe_load(f)
    except FileNotFoundError:
        log.warning(
            f"Cannot open resource file '{variable_substitutions_path}'. "
            f"Proceeding with normalization, but there's a risk that variable names will not be recognized."
        )
        return
    
    rows = swob_ml_normalize(
        file_stream, "EC_raw", station_id_attr="climate_station_number"
    )

    for row in rows:
        if row.variable_name in variable_substitutions:
            yield Row(
                time=row.time,
                val=row.val,
                variable_name=variable_substitutions[row.variable_name],
                unit=row.unit,
                network_name=row.network_name,
                station_id=row.station_id,
                lat=row.lat,
                lon=row.lon,
            )
        else:
            yield row
