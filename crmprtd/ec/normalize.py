from crmprtd.swob_ml import normalize as swob_ml_normalize


def normalize(file_stream):
    return swob_ml_normalize(
        file_stream,
        'EC_raw',
        station_id_attr='climate_station_number'
    )
