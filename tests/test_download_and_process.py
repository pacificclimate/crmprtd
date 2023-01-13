import datetime

import pytest

from scripts.download_and_process import log_filename, cache_filename


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
    ]
)
def test_log_filename(network_name, frequency, province, expected):
    assert log_filename(
        network_name=network_name,
        tag="tag",
        frequency=frequency,
        province=province,
    ) == expected


@pytest.mark.parametrize(
    "network_name, frequency, province, expected",
    [
        # A representative sample, covering all present execution scripts.
        ("bc_hydro", None, None, "~/bc_hydro/cache/tag_bc_hydro_2020-01-02T03:04:05.txt"),
        ("crd", None, None, "~/crd/cache/tag_crd_2020-01-02T03:04:05.txt"),
        ("ec", "freq", "PR", "~/ec/download/tag_freq_pr_2020-01-02T03:04:05.xml"),
        ("bc_env_snow", None, None, "~/bc_env_snow/cache/tag_bc_env_snow_2020-01-02T03:04:05.xml"),
        ("moti", None, None, "~/moti/cache/tag_moti_2020-01-02T03:04:05.txt"),
        ("wamr", None, None, "~/wamr/cache/tag_wamr_2020-01-02T03:04:05.txt"),
        ("wmb", None, None, "~/wmb/download/tag_wmb_2020-01-02T03:04:05.txt"),
        ("nt_forestry", None, None, "~/nt_forestry/cache/tag_nt_forestry_2020-01-02T03:04:05.xml"),
    ]
)
def test_cache_filename(network_name, frequency, province, expected):
    assert cache_filename(
        timestamp=datetime.datetime(2020, 1, 2, 3, 4 , 5, 6),
        network_name=network_name,
        tag="tag",
        frequency=frequency,
        province=province,
    ) == expected
