import datetime

import pytest

from scripts.download_and_process import log_filename, cache_filename, download_args


@pytest.mark.parametrize(
    "network_name, frequency, province, expected",
    [
        # A representative sample, covering all present execution scripts.
        ("bc_hydro", None, None, "~/bc_hydro/logs/tag_bc_hydro_json.log"),
        ("crd", None, None, "~/crd/logs/tag_crd_json.log"),
        ("ec", "freq", "PR", "~/ec/logs/tag_pr_freq_json.log"),
        ("bc_env_snow", None, None, "~/bc_env_snow/logs/tag_bc_env_snow_json.log"),
        ("moti", None, None, "~/moti/logs/tag_moti_json.log"),
        ("wamr", None, None, "~/wamr/logs/tag_wamr_json.log"),
        ("wmb", None, None, "~/wmb/logs/tag_mof_json.log"),
        ("nt_forestry", None, None, "~/nt_forestry/logs/tag_nt_forestry_json.log"),
    ],
)
def test_log_filename(network_name, frequency, province, expected):
    assert (
        log_filename(
            network_name=network_name,
            tag="tag",
            frequency=frequency,
            province=province,
        )
        == expected
    )


@pytest.mark.parametrize(
    "network_name, frequency, province, expected",
    [
        # A representative sample, covering all present execution scripts.
        (
            "bc_hydro",
            None,
            None,
            "~/bc_hydro/cache/tag_bc_hydro_2020-01-02T03:04:05.txt",
        ),
        ("crd", None, None, "~/crd/cache/tag_crd_2020-01-02T03:04:05.txt"),
        ("ec", "freq", "PR", "~/ec/download/tag_freq_pr_2020-01-02T03:04:05.xml"),
        (
            "bc_env_snow",
            None,
            None,
            "~/bc_env_snow/cache/tag_bc_env_snow_2020-01-02T03:04:05.xml",
        ),
        ("moti", None, None, "~/moti/cache/tag_moti_2020-01-02T03:04:05.txt"),
        ("wamr", None, None, "~/wamr/cache/tag_wamr_2020-01-02T03:04:05.txt"),
        ("wmb", None, None, "~/wmb/download/tag_wmb_2020-01-02T03:04:05.txt"),
        (
            "nt_forestry",
            None,
            None,
            "~/nt_forestry/cache/tag_nt_forestry_2020-01-02T03:04:05.xml",
        ),
    ],
)
def test_cache_filename(network_name, frequency, province, expected):
    assert (
        cache_filename(
            timestamp=datetime.datetime(2020, 1, 2, 3, 4, 5),
            network_name=network_name,
            tag="tag",
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
