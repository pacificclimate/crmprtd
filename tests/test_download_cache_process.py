import datetime

import pytest

from crmprtd.download_cache_process import (
    default_log_filename,
    default_cache_filename,
    download_args,
)


@pytest.mark.parametrize(
    "network_name, tag, frequency, province, expected",
    [
        # A representative sample, copied from all present execution scripts.
        # Some changes due to simplification of filename pattern.
        ("bc_hydro", "tag", None, None, "~/bc_hydro/logs/tag_bc_hydro_json.log"),
        ("crd", "tag", None, None, "~/crd/logs/tag_crd_json.log"),
        ("ec", "tag", "freq", "PR", "~/ec/logs/tag_pr_freq_json.log"),
        (
            "bc_env_snow",
            "tag",
            None,
            None,
            "~/bc_env_snow/logs/tag_bc_env_snow_json.log",
        ),
        ("moti", "tag", None, None, "~/moti/logs/tag_moti_json.log"),
        ("wamr", "tag", None, None, "~/wamr/logs/tag_wamr_json.log"),
        ("wmb", "tag", None, None, "~/wmb/logs/tag_wmb_json.log"),
        (
            "nt_forestry",
            "tag",
            None,
            None,
            "~/nt_forestry/logs/tag_nt_forestry_json.log",
        ),
        # And one with no tag
        ("nt_forestry", None, None, None, "~/nt_forestry/logs/nt_forestry_json.log"),
    ],
)
def test_default_log_filename(network_name, tag, frequency, province, expected):
    assert (
        default_log_filename(
            network_name=network_name,
            tag=tag,
            frequency=frequency,
            province=province,
        )
        == expected
    )


@pytest.mark.parametrize(
    "network_name, tag, frequency, province, expected",
    [
        # A representative sample, copied from all present execution scripts.
        # Some changes due to simplification of filename pattern.
        (
            "bc_hydro",
            "tag",
            None,
            None,
            "~/bc_hydro/cache/tag_bc_hydro_2020-01-02T03:04:05.txt",
        ),
        ("crd", "tag", None, None, "~/crd/cache/tag_crd_2020-01-02T03:04:05.txt"),
        ("ec", "tag", "freq", "PR", "~/ec/cache/tag_freq_pr_2020-01-02T03:04:05.xml"),
        (
            "bc_env_snow",
            "tag",
            None,
            None,
            "~/bc_env_snow/cache/tag_bc_env_snow_2020-01-02T03:04:05.xml",
        ),
        ("moti", "tag", None, None, "~/moti/cache/tag_moti_2020-01-02T03:04:05.txt"),
        ("wamr", "tag", None, None, "~/wamr/cache/tag_wamr_2020-01-02T03:04:05.txt"),
        ("wmb", "tag", None, None, "~/wmb/cache/tag_wmb_2020-01-02T03:04:05.txt"),
        (
            "nt_forestry",
            "tag",
            None,
            None,
            "~/nt_forestry/cache/tag_nt_forestry_2020-01-02T03:04:05.xml",
        ),
        (
            "nt_forestry",
            None,
            None,
            None,
            "~/nt_forestry/cache/nt_forestry_2020-01-02T03:04:05.xml",
        ),
    ],
)
def test_default_cache_filename(network_name, tag, frequency, province, expected):
    assert (
        default_cache_filename(
            timestamp=datetime.datetime(2020, 1, 2, 3, 4, 5),
            network_name=network_name,
            tag=tag,
            frequency=frequency,
            province=province,
        )
        == expected
    )


@pytest.mark.parametrize(
    "network_name, frequency, province, time, expected",
    [
        # A representative sample, covering all present execution scripts.
        (
            "bc_hydro",
            None,
            None,
            None,
            [
                "-N",
                "bc_hydro",
                "-f",
                "sftp2.bchydro.com",
                "-F",
                "pcic",
                "-S",
                "~/.ssh/id_rsa",
            ],
        ),
        (
            "crd",
            None,
            None,
            None,
            ["-N", "crd", "--auth_fname", "~/.rtd_auth.yaml", "--auth_key=crd"],
        ),
        ("ec", "freq", "PR", None, ["-N", "ec", "-p", "pr", "-F", "freq"]),
        (
            "bc_env_snow",
            None,
            None,
            datetime.datetime(2020, 1, 2, 3, 4, 5),
            ["-N", "bc_env_snow", "-d", '"2020/01/02 11:00:00"'],
        ),
        (
            "moti",
            None,
            None,
            None,
            [
                "-N",
                "moti",
                "-u",
                "https://prdoas5.apps.th.gov.bc.ca/saw-data/sawr7110",
                "--auth_fname",
                "~/.rtd_auth.yaml",
                "--auth_key=moti",
            ],
        ),
        ("wamr", None, None, None, ["-N", "wamr"]),
        (
            "wmb",
            None,
            None,
            None,
            ["-N", "wmb", "--auth_fname", "~/.rtd_auth.yaml", "--auth_key=wmb"],
        ),
        (
            "nt_forestry",
            None,
            None,
            datetime.datetime(2020, 1, 2, 3, 4, 5),
            ["-N", "nt_forestry", "-d", '"2020/01/02 11:00:00"'],
        ),
    ],
)
def test_download_args(network_name, frequency, province, time, expected):
    assert (
        download_args(
            time=time,
            network_name=network_name,
            tag="tag",
            frequency=frequency,
            province=province,
        )
        == expected
    )
