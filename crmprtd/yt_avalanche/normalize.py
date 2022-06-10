from crmprtd.swob_ml import normalize as normalize_swob


def strip_stn_prefix(stn_id):
    return stn_id.replace("YAA_", "")


def normalize(file_stream):
    yield from normalize_swob(
        file_stream,
        "YAA",
        station_id_attr="msc_id",
        station_id_xform=strip_stn_prefix,
    )
