import datetime
import re
from itertools import product
from typing import List

import pytest

from crmprtd.download_cache_process import (
    default_log_filename,
    default_cache_filename,
    download_args,
    main,
    network_aliases,
)


@pytest.mark.parametrize(
    "network_name, frequency, province, expected",
    [
        # A representative sample, copied from all present execution scripts.
        # Some changes due to simplification of filename pattern.
        ("bc_hydro", None, None, "~/bc_hydro/logs/tag_bc_hydro_json.log"),
        ("crd", None, None, "~/crd/logs/tag_crd_json.log"),
        ("ec", "freq", "PR", "~/ec/logs/tag_pr_freq_json.log"),
        ("bc_env_snow", None, None, "~/bc_env_snow/logs/tag_bc_env_snow_json.log"),
        ("moti", None, None, "~/moti/logs/tag_moti_json.log"),
        ("wamr", None, None, "~/wamr/logs/tag_wamr_json.log"),
        ("wmb", None, None, "~/wmb/logs/tag_wmb_json.log"),
        ("nt_forestry", None, None, "~/nt_forestry/logs/tag_nt_forestry_json.log"),
    ],
)
def test_default_log_filename(network_name, frequency, province, expected):
    assert (
        default_log_filename(
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
        # A representative sample, copied from all present execution scripts.
        # Some changes due to simplification of filename pattern.
        (
            "bc_hydro",
            None,
            None,
            "~/bc_hydro/cache/tag_bc_hydro_2020-01-02T03:04:05.txt",
        ),
        ("crd", None, None, "~/crd/cache/tag_crd_2020-01-02T03:04:05.txt"),
        ("ec", "freq", "PR", "~/ec/cache/tag_freq_pr_2020-01-02T03:04:05.xml"),
        (
            "bc_env_snow",
            None,
            None,
            "~/bc_env_snow/cache/tag_bc_env_snow_2020-01-02T03:04:05.xml",
        ),
        ("moti", None, None, "~/moti/cache/tag_moti_2020-01-02T03:04:05.txt"),
        ("wamr", None, None, "~/wamr/cache/tag_wamr_2020-01-02T03:04:05.txt"),
        ("wmb", None, None, "~/wmb/cache/tag_wmb_2020-01-02T03:04:05.txt"),
        (
            "nt_forestry",
            None,
            None,
            "~/nt_forestry/cache/tag_nt_forestry_2020-01-02T03:04:05.xml",
        ),
    ],
)
def test_default_cache_filename(network_name, frequency, province, expected):
    assert (
        default_cache_filename(
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
            r"~/bc_hydro/cache/tag_bc_hydro_.*\.txt",
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
                    for network in network_aliases[alias]
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
def test_main(
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
    main(arglist.split())
    call_args_list = cp.call_args_list

    # call_args_list is a list of the arguments of calls to chain_subprocessses
    # from each element of that arguments list we extract the first argument
    #   (which is a list of the commands to be chained)
    # seq_of_expected_cmds_prefixes is a list of expected prefixes (initial elements)
    #   of commands
    # we compare actual commands to the prefixes.

    # print("###")
    # print("call_args_list", call_args_list)

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
