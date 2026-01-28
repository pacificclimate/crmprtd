from crmprtd.swob_ml import normalize as swob_ml_normalize



# TODO: Potentially check and store ECCC data flags for quality control of data

def normalize(file_stream):
    return swob_ml_normalize(
        file_stream, "ec_raw", station_id_attr="climate_station_number"
    )
