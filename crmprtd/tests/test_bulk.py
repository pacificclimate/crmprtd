import datetime
import sys
from unittest.mock import Mock, patch
import pytest
from crmprtd import bulk_pipeline
from crmprtd.bulk_pipeline import main, run, process


@pytest.mark.parametrize(
    "network, frequency, stime, etime, tag, directory, expected_calls",
    [
        # Test hourly frequency processing
        (
            "bc_hydro",
            "hourly", 
            "2020-01-01 00:00:00",
            "2020-01-01 02:00:00",
            "test_tag",
            None,
            3,  # Should call process 3 times (00:00, 01:00, 02:00)
        ),
        # Test daily frequency processing
        (
            "crd",
            "daily",
            "2020-01-01 00:00:00", 
            "2020-01-03 00:00:00",
            "daily_tag",
            "/tmp/test",
            3,  # Should call process 3 times (01-01, 01-02, 01-03)
        ),
        # Test EC network with province
        (
            "ec",
            "hourly",
            "2020-01-01 00:00:00",
            "2020-01-01 01:00:00", 
            "ec_tag",
            None,
            2,  # Should call process 2 times (00:00, 01:00)
        ),
    ],
)
def test_bulk_pipeline_run(network, frequency, stime, etime, tag, directory, expected_calls, mocker):
    """Test the run function with various network and time configurations."""
    
    # Mock the process function to track calls
    mock_process = mocker.patch("crmprtd.bulk_pipeline.process")
    
    # Mock setup_logging to avoid actual logging setup
    mock_setup_logging = mocker.patch("crmprtd.bulk_pipeline.setup_logging")
    
    # Mock ensure_directory to avoid filesystem operations
    mock_ensure_directory = mocker.patch("crmprtd.bulk_pipeline.ensure_directory")
    
    # Mock get_defaults_module to return a mock with required methods
    mock_defaults = Mock()
    mock_defaults.default_log_filename.return_value = f"~/{network}/logs/{tag}_{network}_json.log"
    mocker.patch("crmprtd.bulk_pipeline.get_defaults_module", return_value=mock_defaults)
    
    # Create mock options object
    opts = Mock()
    opts.network_name = network
    opts.frequency = frequency
    opts.stime = stime
    opts.etime = etime
    opts.tag = tag
    opts.directory = directory
    opts.province = ["bc"] if network == "ec" else None
    opts.log_filename = None
    opts.log_conf = "test_log.yaml"
    opts.error_email = "test@test.com"
    opts.log_level = "INFO"
    opts.delay = 1
    
    # Mock args list
    args = ["--connection_string", "test_dsn"]
    
    # Run the function
    run(opts, args)
    
    # Verify process was called the expected number of times
    assert mock_process.call_count == expected_calls
    
    # Verify setup_logging was called
    mock_setup_logging.assert_called_once()
    
    # Verify ensure_directory was called for log filename
    mock_ensure_directory.assert_called()


@pytest.mark.parametrize(
    "network, tag, frequency, province, directory, time_str, expected_download_cache_process_calls",
    [
        # Test basic network without province
        (
            "bc_hydro",
            "test_tag", 
            None,
            None,
            None,
            "2020-01-01 12:00:00",
            1,
        ),
        # Test EC network with province and frequency
        (
            "ec",
            "ec_tag",
            "daily",
            "bc", 
            None,
            "2020-01-01 12:00:00",
            1,
        ),
        # Test with custom directory
        (
            "crd",
            "dir_tag",
            None,
            None,
            "/custom/dir",
            "2020-01-01 12:00:00", 
            1,
        ),
    ],
)
def test_bulk_pipeline_process(network, tag, frequency, province, directory, time_str, expected_download_cache_process_calls, mocker):
    """Test the process function with various configurations."""
    
    # Mock download_cache_process_main to track calls
    mock_download_cache_process_main = mocker.patch("crmprtd.bulk_pipeline.download_cache_process_main")
    
    # Mock ensure_directory to avoid filesystem operations
    mock_ensure_directory = mocker.patch("crmprtd.bulk_pipeline.ensure_directory")
    

    
    # Create mock options object
    opts = Mock()
    opts.network_name = network
    opts.tag = tag
    opts.frequency = frequency
    opts.province = province
    opts.directory = directory
    opts.log_filename = f"~/{network}/logs/{tag}_{network}_json.log"
    
    # Parse time
    current_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    
    # Mock args list
    args = ["--connection_string", "test_dsn"]
    
    # Run the function
    process(current_time, opts, args)
    
    # Verify download_cache_process_main was called the expected number of times
    assert mock_download_cache_process_main.call_count == expected_download_cache_process_calls
    
    # Verify the arguments passed to download_cache_process_main
    call_args = mock_download_cache_process_main.call_args[0][0]
    assert "--network" in call_args
    assert network in call_args
    assert "--time" in call_args
    assert time_str in call_args
    
    if tag:
        assert "--tag" in call_args
        assert tag in call_args
        
    if frequency and network == "ec":
        assert "--frequency" in call_args
        assert frequency in call_args
        
    if province and network == "ec":
        assert "--province" in call_args
        assert province in call_args
        
    if directory:
        assert "--cache_filename" in call_args
        mock_ensure_directory.assert_called()


@pytest.mark.parametrize(
    "network, additional_args, expected_network_calls",
    [
        # Test single network
        ("bc_hydro", ["--tag", "test", "--frequency", "hourly"], 1),
        # Test network alias - should process multiple networks
        ("hourly_swobml2", ["--tag", "alias_test"], len(bulk_pipeline.network_aliases.get("hourly_swobml2", []))),
        # Test EC network with province
        ("ec", ["--tag", "ec_test", "--frequency", "daily", "--province", "bc"], 1),
    ],
)
def test_bulk_pipeline_main(network, additional_args, expected_network_calls, mocker):
    """Test the main function with various network configurations."""
    
    # Mock the run function to track calls
    mock_run = mocker.patch("crmprtd.bulk_pipeline.run")
    
    # Mock get_defaults_module to return a mock with required methods  
    mock_defaults = Mock()
    mock_defaults.default_end_time.return_value = "2020-01-02 00:00:00"
    mocker.patch("crmprtd.bulk_pipeline.get_defaults_module", return_value=mock_defaults)
    
    # Mock files function for default log config
    mock_files = mocker.patch("crmprtd.bulk_pipeline.files")
    mock_files.return_value.__truediv__.return_value = "default_log.yaml"
    
    # Mock add_province_args for EC network
    mock_add_province_args = mocker.patch("crmprtd.bulk_pipeline.add_province_args")
    
    # Prepare test arguments
    test_args = [
        "--network", network,
        "--start_date", "2020-01-01 00:00:00", 
        "--end_date", "2020-01-01 23:00:00",

    ] + additional_args
    
    # Mock sys.argv
    with patch.object(sys, 'argv', ['bulk_pipeline.py'] + test_args):
        # Run main function
        main()
    
    # Verify run was called the expected number of times
    assert mock_run.call_count == expected_network_calls
    
    # If EC network, verify add_province_args was called
    if network == "ec":
        mock_add_province_args.assert_called()


@pytest.mark.parametrize(
    "network, frequency, error_type",
    [
        # Test invalid time format
        ("bc_hydro", "hourly", "time_parse_error"),
        # Test invalid frequency  
        ("crd", "invalid_freq", "frequency_error"),
    ],
)
def test_bulk_pipeline_error_handling(network, frequency, error_type, mocker):
    """Test error handling in bulk pipeline functions."""
    
    # Mock logging
    mock_logger = Mock()
    mocker.patch("crmprtd.bulk_pipeline.logging.getLogger", return_value=mock_logger)
    
    # Mock setup_logging
    mock_setup_logging = mocker.patch("crmprtd.bulk_pipeline.setup_logging")
    
    # Mock get_defaults_module
    mock_defaults = Mock()
    mock_defaults.default_log_filename.return_value = f"~/{network}/logs/test_{network}_json.log"
    mocker.patch("crmprtd.bulk_pipeline.get_defaults_module", return_value=mock_defaults)
    
    # Mock ensure_directory
    mocker.patch("crmprtd.bulk_pipeline.ensure_directory")
    
    # Create mock options with invalid data
    opts = Mock()
    opts.network_name = network
    opts.frequency = frequency
    opts.log_filename = None
    opts.tag = "test"
    opts.province = None
    opts.log_conf = "test_log.yaml"
    opts.error_email = "test@test.com"
    opts.log_level = "INFO"
    opts.delay = 1
    
    if error_type == "time_parse_error":
        opts.stime = "invalid-time-format"
        opts.etime = "2020-01-01 23:00:00"
    elif error_type == "frequency_error":
        opts.stime = "2020-01-01 00:00:00"
        opts.etime = "2020-01-01 23:00:00"
        # frequency is already set to invalid value
    
    args = []
    
    # Run function and expect it to handle the error gracefully
    run(opts, args)
    
    # Verify that error was logged
    mock_logger.error.assert_called()


def test_bulk_pipeline_time_range_processing(mocker):
    """Test that time ranges are processed correctly with proper intervals."""
    
    # Mock process function to track individual calls
    mock_process = mocker.patch("crmprtd.bulk_pipeline.process")
    
    # Mock other dependencies
    mocker.patch("crmprtd.bulk_pipeline.setup_logging")
    mocker.patch("crmprtd.bulk_pipeline.ensure_directory")
    
    mock_defaults = Mock()
    mock_defaults.default_log_filename.return_value = "~/test/logs/test_log.log"
    mocker.patch("crmprtd.bulk_pipeline.get_defaults_module", return_value=mock_defaults)
    
    mock_logger = Mock()
    mocker.patch("crmprtd.bulk_pipeline.logging.getLogger", return_value=mock_logger)
    
    # Test hourly processing
    opts = Mock()
    opts.network_name = "bc_hydro"
    opts.frequency = "hourly"
    opts.stime = "2020-01-01 00:00:00"
    opts.etime = "2020-01-01 03:00:00"  # 4 hours total
    opts.tag = "hourly_test"
    opts.directory = None
    opts.province = None
    opts.log_filename = None
    opts.log_conf = "test.yaml"
    opts.error_email = "test@test.com"
    opts.log_level = "INFO"
    opts.delay = 0  # No delay for testing
    
    args = []
    
    # Run the function
    run(opts, args)
    
    # Should be called 4 times (00:00, 01:00, 02:00, 03:00)
    assert mock_process.call_count == 4
    
    # Verify the timestamps passed to process function
    call_times = [call[0][0] for call in mock_process.call_args_list]
    expected_times = [
        datetime.datetime(2020, 1, 1, 0, 0, 0),
        datetime.datetime(2020, 1, 1, 1, 0, 0), 
        datetime.datetime(2020, 1, 1, 2, 0, 0),
        datetime.datetime(2020, 1, 1, 3, 0, 0),
    ]
    
    assert call_times == expected_times


def test_bulk_pipeline_network_alias_handling(mocker):
    """Test that network aliases are properly expanded to individual networks."""
    
    # Mock the run function to track calls per network
    mock_run = mocker.patch("crmprtd.bulk_pipeline.run")
    
    # Mock dependencies
    mock_defaults = Mock()
    mock_defaults.default_end_time.return_value = "2020-01-02 00:00:00"
    mocker.patch("crmprtd.bulk_pipeline.get_defaults_module", return_value=mock_defaults)
    
    mocker.patch("crmprtd.bulk_pipeline.files")
    
    # Test with a network alias that maps to multiple networks
    test_alias = "hourly_swobml2"
    expected_networks = bulk_pipeline.network_aliases.get(test_alias, [])
    
    test_args = [
        "--network", test_alias,
        "--stime", "2020-01-01 00:00:00",
        "--etime", "2020-01-01 01:00:00",
        "--frequency", "hourly",
    ]
    
    with patch.object(sys, 'argv', ['bulk_pipeline.py'] + test_args):
        main()
    
    # Should call run once for each network in the alias
    assert mock_run.call_count == len(expected_networks)
    
    # Verify each network was processed
    called_networks = [call[0][0].network_name for call in mock_run.call_args_list]
    assert set(called_networks) == set(expected_networks)