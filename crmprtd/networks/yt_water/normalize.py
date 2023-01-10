from crmprtd.swob_ml import normalize as normalize_swob


def strip_stn_prefix(stn_id):
    return stn_id.replace("YT-DE-WRB_", "")


def normalize(file_stream):
    yield from normalize_swob(
        file_stream,
        "YWR",
        station_id_attr="msc_id",
        station_id_xform=strip_stn_prefix,
    )
