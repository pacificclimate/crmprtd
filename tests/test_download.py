from importlib import import_module

import pytest
import crmprtd.download
from crmprtd import NETWORKS


@pytest.mark.parametrize("network", NETWORKS)
def test_network_dispatch(network, mocker):
    """Exercise the dispatcher and test that it dispatches correctly."""

    dl_module_name = f"crmprtd.networks.{network}.download"

    # Catch the call to the targeted downloader
    mocker.patch(f"{dl_module_name}.main")

    # Dispatch
    arglist = f"-N {network} -X eks -Y why -Z zed".split()
    crmprtd.download.main(arglist)

    # Check that targeted downloader was called with the expected args
    downloader = import_module(dl_module_name).main
    downloader.assert_called_once()
    assert downloader.call_args.kwargs["arglist"] == arglist
