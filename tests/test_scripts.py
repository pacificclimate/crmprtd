from datetime import datetime

import pytest
import pytz

import crmprtd
from crmprtd import get_version
from crmprtd.download_utils import verify_date

# Must import the module, not objects from it, so we can mock the objects.
import crmprtd.process
import crmprtd.download


@pytest.mark.parametrize(
    "name",
    [
        "crmprtd_pipeline",
        "crmprtd_download",
        "crmprtd_process",
        "crmprtd_infill_all",
    ],
)
def test_version_option(capsys, name):
    """Test that CLI scripts accept --version arg and return the expected value."""
    entry_point = crmprtd.pkg_resources.get_entry_map("crmprtd")["console_scripts"][
        name
    ].load()
    with pytest.raises(SystemExit):
        entry_point(["--version"])
    captured = capsys.readouterr()
    assert captured.out == f"{get_version()}\n"


@pytest.mark.parametrize(
    "network, other_args",
    [
        # Non-SWOB networks
        ("bc_hydro", "".split()),
        ("crd", "--username u --password p".split()),
        ("ec", "-F daily".split()),
        ("moti", "--username u --password p".split()),
        ("wamr", "".split()),
        ("wmb", "--username u --password p".split()),
        # A SWOB network
        (crmprtd.SWOB_PARTNERS[0], "".split()),
    ],
)
def test_download_main(network, other_args, mocker):
    """
    Test that per-network `main`s don't error out when given reasonable args.
    This test could be more comprehensive ... but more work.
    """
    args = ["-N", network] + other_args

    nw = "ec_swob" if network in crmprtd.SWOB_PARTNERS else network
    pd = mocker.patch(f"crmprtd.networks.{nw}.download.download")

    crmprtd.download.main(args)

    pd.assert_called_once()


@pytest.mark.parametrize(
    "connection_string, sample_size, network, start_date, end_date, infer, diagnostic",
    [
        ("DSN", "99", "crd", "2000-01-01", "2000-02-01", False, False),
    ],
)
def test_process_main(
    connection_string,
    sample_size,
    network,
    start_date,
    end_date,
    infer,
    diagnostic,
    mocker,
):
    """Test that crmprtd.process.main works with some plausible args."""
    args = []
    if connection_string is not None:
        args += ["-c", connection_string]
    if sample_size is not None:
        args += ["--sample_size", sample_size]
    if network is not None:
        args += ["-N", network]
    if start_date is not None:
        args += ["-S", start_date]
    if end_date is not None:
        args += ["-E", end_date]
    if infer:
        args += ["-I"]
    if diagnostic:
        args += ["-D"]

    pp = mocker.patch("crmprtd.process.process")

    crmprtd.process.main(args)

    assert pp.called_with(
        connection_string=connection_string,
        sample_size=sample_size,
        network=network,
        start_date=pytz.utc.localize(verify_date(start_date, datetime.min)),
        end_date=pytz.utc.localize(verify_date(end_date, datetime.max)),
        is_diagnostic=diagnostic,
        do_infer=infer,
    )
