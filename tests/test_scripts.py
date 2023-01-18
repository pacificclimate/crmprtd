import pytest
import crmprtd
from crmprtd import get_version


@pytest.mark.parametrize(
    "name",
    [
        "crmprtd_dcp",
        "crmprtd_download",
        "crmprtd_process",
        "crmprtd_infill_all",
    ],
)
def test_version_option(capsys, name):
    entry_point = crmprtd.pkg_resources.get_entry_map("crmprtd")["console_scripts"][
        name
    ].load()
    with pytest.raises(SystemExit):
        entry_point(["--version"])
    captured = capsys.readouterr()
    assert captured.out == f"{get_version()}\n"
