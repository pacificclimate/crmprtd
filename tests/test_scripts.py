import pytest
import crmprtd
from crmprtd import get_version, download, NETWORKS


@pytest.mark.parametrize("network", NETWORKS)
def test_version_download(capsys, network):
    download.main(["-N", network, "--version"])
    captured = capsys.readouterr()
    assert captured.out == f"{get_version()}\n"


@pytest.mark.parametrize("name", ["crmprtd_process", "crmprtd_infill_all"])
def test_version_non_download(capsys, name):
    entry_point = crmprtd.pkg_resources.get_entry_map("crmprtd")["console_scripts"][
        name
    ].load()
    entry_point(["--version"])
    captured = capsys.readouterr()
    assert captured.out == f"{get_version()}\n"
