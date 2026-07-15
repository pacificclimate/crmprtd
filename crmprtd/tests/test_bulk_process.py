"""Tests for crmprtd.bulk_process.

These exercise the file-selection, batching, aggregation, and error-handling
logic of the bulk processor. The actual per-file pipeline (crmprtd.process.process)
is mocked out so the tests need no database or network normalizers.
"""

import os
from argparse import Namespace
from datetime import datetime

import pytest
import pytz

import crmprtd.bulk_process as bp


def make_opts(**overrides):
    """A fully-populated opts Namespace with harmless defaults.

    run() reads a fixed set of attributes; provide them all so individual tests
    only need to override what they care about.
    """
    opts = Namespace(
        # file selection
        directory=None,
        file_pattern="*.xml",
        filename=None,
        file_list=None,
        # logging (setup_logging is mocked in these tests)
        log_filename=None,
        log_conf=None,
        error_email=None,
        log_level="INFO",
        # process/insert args
        connection_string=None,
        sample_size=50,
        network="wmb",
        diag=False,
        infer=False,
        insert_strategy="BULK",
        bulk_chunk_size=1000,
        start_date=None,
        end_date=None,
        # bulk behaviour
        move_processed=False,
        force=False,
    )
    for key, value in overrides.items():
        setattr(opts, key, value)
    return opts


@pytest.fixture(autouse=True)
def no_logging_setup(mocker):
    """setup_logging touches the filesystem and reconfigures logging globally;
    stub it out for every test in this module."""
    mocker.patch.object(bp, "setup_logging")


# ---------------------------------------------------------------------------
# resolve_files
# ---------------------------------------------------------------------------


def test_resolve_files_directory_default_pattern(tmp_path):
    (tmp_path / "a.xml").write_text("")
    (tmp_path / "b.xml").write_text("")
    (tmp_path / "c.txt").write_text("")

    opts = make_opts(directory=str(tmp_path))
    found = bp.resolve_files(opts)

    assert sorted(os.path.basename(f) for f in found) == ["a.xml", "b.xml"]


def test_resolve_files_directory_custom_pattern(tmp_path):
    (tmp_path / "a.xml").write_text("")
    (tmp_path / "c.txt").write_text("")

    opts = make_opts(directory=str(tmp_path), file_pattern="*.txt")
    found = bp.resolve_files(opts)

    assert [os.path.basename(f) for f in found] == ["c.txt"]


def test_resolve_files_single_filename():
    opts = make_opts(filename="/some/path/data.xml")
    assert bp.resolve_files(opts) == ["/some/path/data.xml"]


def test_resolve_files_file_list(tmp_path):
    listing = tmp_path / "list.txt"
    listing.write_text("/one.xml\n  /two.xml  \n\n/three.xml\n")

    opts = make_opts(file_list=str(listing))
    assert bp.resolve_files(opts) == ["/one.xml", "/two.xml", "/three.xml"]


def test_resolve_files_no_selection_raises():
    opts = make_opts()
    with pytest.raises(ValueError):
        bp.resolve_files(opts)


def test_resolve_files_directory_takes_precedence(tmp_path):
    """directory wins over filename/file_list when several are given."""
    (tmp_path / "a.xml").write_text("")
    opts = make_opts(directory=str(tmp_path), filename="/ignored.xml")
    found = bp.resolve_files(opts)
    assert [os.path.basename(f) for f in found] == ["a.xml"]


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


def make_files(tmp_path, *names):
    paths = []
    for name in names:
        p = tmp_path / name
        p.write_text("<xml/>")
        paths.append(str(p))
    return paths


def test_run_processes_each_file(tmp_path, mocker):
    files = make_files(tmp_path, "a.xml", "b.xml")
    proc = mocker.patch.object(
        bp, "process", return_value={"successes": 1, "skips": 0, "failures": 0}
    )

    rc = bp.run(make_opts(directory=str(tmp_path)))

    assert rc == 0
    assert proc.call_count == 2


def test_run_passes_expected_process_arguments(tmp_path, mocker):
    make_files(tmp_path, "a.xml")
    proc = mocker.patch.object(
        bp, "process", return_value={"successes": 1, "skips": 0, "failures": 0}
    )

    opts = make_opts(
        directory=str(tmp_path),
        network="wmb",
        sample_size=7,
        bulk_chunk_size=42,
        infer=True,
        diag=False,
        insert_strategy="SINGLE",
    )
    bp.run(opts)

    _, kwargs = proc.call_args
    assert kwargs["network"] == "wmb"
    assert kwargs["sample_size"] == 7
    assert kwargs["bulk_chunk_size"] == 42
    assert kwargs["do_infer"] is True
    assert kwargs["is_diagnostic"] is False
    assert kwargs["insert_strategy"] == bp.InsertStrategy.SINGLE
    # Unbounded date window by default.
    assert kwargs["start_date"] == pytz.utc.localize(datetime.min)
    assert kwargs["end_date"] == pytz.utc.localize(datetime.max)
    # A binary stream is handed to process.
    assert "b" in kwargs["input_stream"].mode


def test_run_localizes_explicit_dates(tmp_path, mocker):
    make_files(tmp_path, "a.xml")
    proc = mocker.patch.object(
        bp, "process", return_value={"successes": 0, "skips": 0, "failures": 0}
    )

    bp.run(
        make_opts(
            directory=str(tmp_path), start_date="2022-06-01", end_date="2022-06-18"
        )
    )

    _, kwargs = proc.call_args
    assert kwargs["start_date"] == pytz.utc.localize(datetime(2022, 6, 1))
    assert kwargs["end_date"] == pytz.utc.localize(datetime(2022, 6, 18))


def test_run_skips_nonexistent_files(tmp_path, mocker):
    files = make_files(tmp_path, "a.xml")
    listing = tmp_path / "list.txt"
    listing.write_text(f"{files[0]}\n{tmp_path}/missing.xml\n")
    proc = mocker.patch.object(
        bp, "process", return_value={"successes": 1, "skips": 0, "failures": 0}
    )

    rc = bp.run(make_opts(file_list=str(listing)))

    assert rc == 0
    assert proc.call_count == 1


def test_run_no_valid_files_returns_zero(tmp_path, mocker):
    listing = tmp_path / "list.txt"
    listing.write_text(f"{tmp_path}/missing.xml\n")
    proc = mocker.patch.object(bp, "process")

    rc = bp.run(make_opts(file_list=str(listing)))

    assert rc == 0
    proc.assert_not_called()


def test_run_aggregates_totals(tmp_path, mocker, caplog):
    make_files(tmp_path, "a.xml", "b.xml")
    mocker.patch.object(
        bp,
        "process",
        side_effect=[
            {"successes": 3, "skips": 1, "failures": 0},
            {"successes": 2, "skips": 0, "failures": 4},
        ],
    )

    with caplog.at_level("INFO", "crmprtd"):
        bp.run(make_opts(directory=str(tmp_path)))

    summary = next(
        r for r in caplog.records if r.getMessage() == "Bulk insertion results"
    )
    results = summary.results
    assert results["successes"] == 5
    assert results["skips"] == 1
    assert results["failures"] == 4
    assert results["files"] == 2
    assert results["files_succeeded"] == 2
    assert results["files_failed"] == 0


def test_run_tolerates_none_results_from_diagnostic(tmp_path, mocker, caplog):
    """Diagnostic runs return None; totals must stay at zero, not raise."""
    make_files(tmp_path, "a.xml")
    mocker.patch.object(bp, "process", return_value=None)

    with caplog.at_level("INFO", "crmprtd"):
        rc = bp.run(make_opts(directory=str(tmp_path), diag=True))

    assert rc == 0
    summary = next(
        r for r in caplog.records if r.getMessage() == "Bulk insertion results"
    )
    assert summary.results["successes"] == 0
    assert summary.results["files_succeeded"] == 1


def test_run_move_processed(tmp_path, mocker):
    files = make_files(tmp_path, "a.xml", "b.xml")
    mocker.patch.object(
        bp, "process", return_value={"successes": 1, "skips": 0, "failures": 0}
    )

    bp.run(make_opts(directory=str(tmp_path), move_processed=True))

    processed = tmp_path / "processed"
    assert (processed / "a.xml").exists()
    assert (processed / "b.xml").exists()
    for f in files:
        assert not os.path.exists(f)


def test_run_does_not_move_when_disabled(tmp_path, mocker):
    files = make_files(tmp_path, "a.xml")
    mocker.patch.object(
        bp, "process", return_value={"successes": 1, "skips": 0, "failures": 0}
    )

    bp.run(make_opts(directory=str(tmp_path), move_processed=False))

    assert os.path.exists(files[0])
    assert not (tmp_path / "processed").exists()


def test_run_stops_on_failure_without_force(tmp_path, mocker):
    make_files(tmp_path, "a.xml", "b.xml", "c.xml")
    proc = mocker.patch.object(bp, "process", side_effect=RuntimeError("boom"))

    rc = bp.run(make_opts(directory=str(tmp_path), force=False))

    assert rc == 1
    # Stops after the first failing file.
    assert proc.call_count == 1


def test_run_continues_on_failure_with_force(tmp_path, mocker):
    make_files(tmp_path, "a.xml", "b.xml", "c.xml")
    proc = mocker.patch.object(bp, "process", side_effect=RuntimeError("boom"))

    rc = bp.run(make_opts(directory=str(tmp_path), force=True))

    assert rc == 1
    # Attempts every file despite each failing.
    assert proc.call_count == 3


def test_run_failing_file_is_not_moved(tmp_path, mocker):
    files = make_files(tmp_path, "a.xml")
    mocker.patch.object(bp, "process", side_effect=RuntimeError("boom"))

    bp.run(make_opts(directory=str(tmp_path), move_processed=True, force=True))

    # The source file stays put; nothing moved into processed/.
    assert os.path.exists(files[0])
    assert not (tmp_path / "processed" / "a.xml").exists()


def test_run_rolls_back_shared_session_on_failure(tmp_path, mocker):
    make_files(tmp_path, "a.xml")
    session = mocker.MagicMock()
    mocker.patch.object(bp, "create_engine")
    mocker.patch.object(bp, "sessionmaker", return_value=lambda: session)
    mocker.patch.object(bp, "process", side_effect=RuntimeError("boom"))

    bp.run(
        make_opts(
            directory=str(tmp_path), connection_string="postgresql://x", force=True
        )
    )

    session.rollback.assert_called_once()


def test_run_reuses_one_session_across_files(tmp_path, mocker):
    make_files(tmp_path, "a.xml", "b.xml")
    session = mocker.MagicMock()
    mocker.patch.object(bp, "create_engine")
    mocker.patch.object(bp, "sessionmaker", return_value=lambda: session)
    proc = mocker.patch.object(
        bp, "process", return_value={"successes": 1, "skips": 0, "failures": 0}
    )

    bp.run(make_opts(directory=str(tmp_path), connection_string="postgresql://x"))

    # Same session object handed to every process() call.
    sessions = {kwargs["sesh"] for _, kwargs in proc.call_args_list}
    assert sessions == {session}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_requires_network(mocker):
    mocker.patch("sys.argv", ["bulk_process", "-d", "/tmp/whatever"])
    with pytest.raises(SystemExit):
        bp.main()


def test_main_move_processed_defaults_off(tmp_path, mocker):
    captured = {}

    def fake_run(opts):
        captured["opts"] = opts
        return 0

    mocker.patch.object(bp, "run", side_effect=fake_run)
    mocker.patch("sys.argv", ["bulk_process", "-N", "wmb", "-d", str(tmp_path)])

    rc = bp.main()

    assert rc == 0
    assert captured["opts"].move_processed is False
    assert captured["opts"].network == "wmb"
    assert captured["opts"].directory == str(tmp_path)


def test_main_returns_run_exit_code(mocker, tmp_path):
    mocker.patch.object(bp, "run", return_value=1)
    mocker.patch("sys.argv", ["bulk_process", "-N", "wmb", "-d", str(tmp_path)])
    assert bp.main() == 1
