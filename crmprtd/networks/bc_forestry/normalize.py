from crmprtd.swob_ml import normalize as normalize_swob


def normalize(file_stream):
    yield from normalize_swob(file_stream, "FLNRO-WMB", station_id_attr="stn_id")
