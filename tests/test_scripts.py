import pytest
import crmprtd
from crmprtd import get_version


@pytest.mark.parametrize(
    "name, entry_point",
    [
        (name, ep.load()) for name, ep in
        crmprtd.pkg_resources.get_entry_map("crmprtd")["console_scripts"].items()
    ]
)
def test_version(capsys, name, entry_point):
    entry_point(["--version"])
    captured = capsys.readouterr()
    assert captured.out == f"{get_version()}\n"
