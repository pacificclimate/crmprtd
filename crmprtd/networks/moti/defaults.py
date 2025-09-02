from crmprtd.networks import (
    default_log_filename,
    default_cache_filename as default_cache_filename,
)


def default_download_args(**_):
    return "-u https://prdoas5.apps.th.gov.bc.ca/saw-data/sawr7110 --auth_fname ~/.rtd_auth.yaml --auth_key=moti".split()
