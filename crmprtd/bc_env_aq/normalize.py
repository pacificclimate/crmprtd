from crmprtd.swob_ml import normalize as normalize_swob


def normalize(file_stream):
    yield from normalize_swob(file_stream, 'BC_ENV_AQ',
                              station_id_attr='msc_id')
