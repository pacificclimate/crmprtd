import re
from itertools import product
from datetime import datetime
from typing import List

import pytest
import pytz

import crmprtd
from crmprtd import get_version
from crmprtd.download_utils import verify_date

# Must import the module, not objects from it, so we can mock the objects.
import crmprtd.process
import crmprtd.download
import crmprtd.download_cache_process


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


def match_args(arglist: List[str], pattern: str):
    return re.match(pattern, " ".join(arglist))


def assert_match_args(*args):
    assert match_args(*args) is not None


@pytest.mark.parametrize(
    "network, tag, frequency, log_filename, cache_filename, connection_string, "
    "seq_of_expected_cmds_patterns, expected_final_destination_pattern",
    # This covers all current networks and aliases.
    [
        # Tests of all networks, with default log/cache filenames
        (
            "bc_hydro",
            "tag",
            None,
            None,
            None,
            None,
            [
                [
                    r"crmprtd_download -N bc_hydro",
                ],
            ],
            r".*/bc_hydro/cache/tag_bc_hydro_.*\.txt",
        ),
        *(
            (
                network,
                "tag",
                None,
                None,
                None,
                "DSN",
                [
                    [
                        rf"crmprtd_download -N {network}",
                        rf"tee\s+~/{network}/cache/tag_{network}_.*.txt",
                        rf"crmprtd_process -N {network} -c DSN",
                    ],
                ],
                None,
            )
            for network in "crd moti wamr wmb".split()
        ),
        (
            "ec",
            "tag",
            "daily",
            None,
            None,
            "DSN",
            [
                [
                    rf"crmprtd_download -N ec -p {prov} -F daily",
                    rf"tee\s+~/ec/cache/tag_daily_{prov}_.*.xml",
                    r"crmprtd_process -N ec -c DSN",
                ]
                for prov in "bc yt".split()
            ],
            None,
        ),
        *(
            (
                alias,
                "tag",
                None,
                None,
                None,
                "DSN",
                [
                    [
                        rf"crmprtd_download -N {network}",
                        rf"tee\s+~/{network}/cache/tag_{network}_.*.xml",
                        rf"crmprtd_process -N {network} -c DSN",
                    ]
                    for network in crmprtd.download_cache_process.network_aliases[alias]
                ],
                None,
            )
            for alias in "hourly_swobml2 ytnt".split()
        ),
        # Tests of output filename handling
        *(
            (
                network,
                "tag",
                None,
                log_filename,
                cache_filename,
                "DSN",
                [
                    [
                        (
                            rf"crmprtd_download -N {network}"
                            rf" .*--log_filename {log_filename or f'~/{network}/logs/tag_{network}_json.log'}"
                        ),
                        rf"tee\s+{cache_filename or rf'~/{network}/cache/tag_{network}_.*.txt'}",
                        rf"crmprtd_process -N {network} -c DSN",
                    ],
                ],
                None,
            )
            for network, log_filename, cache_filename in product(
                "crd".split(),  # Probably only need to check on one network
                (None, "custom_log_filename"),
                (None, "custom_cache_filename"),
            )
        ),
    ],
)
def test_download_cache_process_main(
    network,
    tag,
    frequency,
    log_filename,
    cache_filename,
    connection_string,
    seq_of_expected_cmds_patterns,
    expected_final_destination_pattern,
    mocker,
):
    arglist = f"-N {network}"
    if tag is not None:
        arglist += f" -T {tag}"
    if frequency is not None:
        arglist += f" -F {frequency}"
    if log_filename is not None:
        arglist += f" --log_filename {log_filename}"
    if cache_filename is not None:
        arglist += f" --cache_filename {cache_filename}"
    if connection_string is not None:
        arglist += f" -c {connection_string}"

    # In certain cases, the unit under test will try to open a file.
    # Instead, don't open a file but return the filepath for checking.
    def new_open(filepath, *args, **kwargs):
        return filepath

    mocker.patch("builtins.open", new=new_open)

    # Mock chain_subprocesses, so that we can see what it is being called with. That's
    # the evidence we use to certify that the script is working as expected.
    # chain_subprocesses itself is tested separately.
    cp = mocker.patch("crmprtd.infill.chain_subprocesses", return_value=True)
    crmprtd.download_cache_process.main(arglist.split())
    call_args_list = cp.call_args_list

    # Note: call_args_list is a list of the arguments of calls to chain_subprocesses
    # from each element of that arguments list we extract the first argument
    #   (which is a list of the commands to be chained)
    # seq_of_expected_cmds_prefixes is a list of expected prefixes (initial elements)
    #   of commands
    # we compare actual commands to the prefixes.

    # Check that the expected number of calls was made.
    assert len(call_args_list) == len(seq_of_expected_cmds_patterns)

    # Check that each call contained the expected commands (or prefixes thereof).
    for call_arg, expected_cmds_patterns in zip(
        call_args_list, seq_of_expected_cmds_patterns
    ):
        commands, *_ = call_arg.args
        final_destination = call_arg.kwargs["final_destination"]
        # Check that the number of commands in the call is as expected.
        assert len(commands) == len(expected_cmds_patterns)
        # Check that each command matches the expected pattern.
        for cmd, expected_cmd_pattern in zip(commands, expected_cmds_patterns):
            assert_match_args(cmd, expected_cmd_pattern)
        # Check that final destination is as expected.
        assert final_destination is None or re.match(
            expected_final_destination_pattern, final_destination
        )

    cp.reset_mock()
