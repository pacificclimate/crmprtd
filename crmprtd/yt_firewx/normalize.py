from crmprtd.swob_ml import normalize as normalize_swob


def strip_stn_prefix(stn_id):
    return stn_id.replace("YT-DCS-WFM_", "")


def normalize(file_stream):
    yield from normalize_swob(
        file_stream,
        "YTF",
        station_id_attr="msc_id",
        station_id_xform=strip_stn_prefix,
    )
