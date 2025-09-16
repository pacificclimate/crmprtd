from crmprtd.networks import (
    default_log_filename,
    default_cache_filename,
    default_time,
    default_end_time
)


def default_download_args(**_):
    return f"-f sftp2.bchydro.com -F pcic -S ~/.ssh/id_rsa".split()
