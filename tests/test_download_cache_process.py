import datetime

import pytest

from crmprtd.download_cache_process import (
    default_log_filename,
    cache_filename,
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
def test_log_filename(network_name, frequency, province, expected):
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
def test_cache_filename(network_name, frequency, province, expected):
    assert (
        cache_filename(
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


@pytest.mark.parametrize(
    "network, tag, connection_string, frequency, seq_of_expected_cmds_prefixes",
    # This covers all current networks and aliases.
    [
        (
            "bc_hydro",
            "tag",
            None,
            None,
            [
                [
                    "crmprtd_download -N bc_hydro".split(),
                ],
            ],
        ),
        *(
            (
                network,
                "tag",
                "DSN",
                None,
                [
                    [
                        f"crmprtd_download -N {network}".split(),
                        "tee".split(),
                        f"crmprtd_process -N {network} -c DSN".split(),
                    ],
                ],
            )
            for network in "crd moti wamr wmb".split()
        ),
        (
            "ec",
            "tag",
            "DSN",
            "daily",
            [
                [
                    f"crmprtd_download -N ec -p {prov} -F daily".split(),
                    "tee".split(),
                    "crmprtd_process -N ec -c DSN".split(),
                ]
                for prov in "bc yt".split()
            ],
        ),
        *(
            (
                alias,
                "tag",
                "DSN",
                None,
                [
                    [
                        f"crmprtd_download -N {network}".split(),
                        "tee".split(),
                        f"crmprtd_process -N {network} -c DSN".split(),
                    ]
                    for network in network_aliases[alias]
                ],
            )
            for alias in "hourly_swobml2 ytnt".split()
        ),
    ],
)
def test_main(
    network, tag, connection_string, frequency, seq_of_expected_cmds_prefixes, mocker
):
    arglist = f"-N {network} -T {tag}"
    if connection_string is not None:
        arglist += f" -c {connection_string}"
    if frequency is not None:
        arglist += f" -F {frequency}"

    # In certain cases, the unit under test will try to open a file, in a place that
    # does not exist. Catch this to prevent an inconsquential error.
    mocker.patch("builtins.open", return_value=None)

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
    assert len(call_args_list) == len(seq_of_expected_cmds_prefixes)

    # Check that each call contained the expected commands (or prefixes thereof).
    for call_arg, expected_cmds_prefixes in zip(
        call_args_list, seq_of_expected_cmds_prefixes
    ):
        commands, *_ = call_arg.args
        # Check that the number of commands in the call is as expected.
        assert len(commands) == len(expected_cmds_prefixes)
        # Check that the prefix of each command is as expected.
        for cmd, expected_cmd in zip(commands, expected_cmds_prefixes):
            assert cmd[: len(expected_cmd)] == expected_cmd

    cp.reset_mock()
