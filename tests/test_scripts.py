import pytest
import crmprtd
from crmprtd import get_version, download, NETWORKS


@pytest.mark.parametrize("network", NETWORKS)
def test_version_download(capsys, network):
    download.main(["-N", network, "--version"])
    captured = capsys.readouterr()
    assert captured.out == f"{get_version()}\n"


@pytest.mark.parametrize(
    "name, entry_point",
    [
        (name, ep.load())
        for name, ep in crmprtd.pkg_resources.get_entry_map("crmprtd")[
            "console_scripts"
        ].items()
        if name != "crmprtd_download"
    ],
)
def test_version_non_download(capsys, name, entry_point):
    entry_point(["--version"])
    captured = capsys.readouterr()
    assert captured.out == f"{get_version()}\n"
