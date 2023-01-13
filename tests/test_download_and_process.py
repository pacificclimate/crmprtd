import pytest

from scripts.download_and_process import log_filename


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
