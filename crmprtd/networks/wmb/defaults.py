from crmprtd.networks import (
    default_log_filename,
    default_cache_filename as default_cache_filename,
)


def default_download_args(**_):
    return "--auth_fname ~/.rtd_auth.yaml --auth_key=wmb".split()
