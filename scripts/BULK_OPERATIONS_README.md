# Bulk Operations Documentation

This document covers the three bulk operation scripts available in the CRMPRTD project for downloading, processing, and pipeline operations on climate and weather data.

## Overview

The bulk operation scripts provide different approaches to handle large-scale data operations:

1. **`bulk_download.py`** - Downloads data files for specified time ranges
2. **`bulk_process.py`** - Processes previously downloaded files 
3. **`bulk_pipeline.py`** - Complete download-and-process pipeline for single networks

## Quick Start

### Complete Pipeline (Recommended)
For most use cases, use the pipeline script for a complete download-and-process operation:

```bash
python scripts/bulk_pipeline.py \
    -N ec \
    -p BC \
    -S "2025-01-01 00:00:00" \
    -E "2025-01-01 23:59:59" \
    -F hourly \
    -c "dbname=rtcrmp user=crmp" # more likely something like "postgresql://crmp@db.pcic.uvic.ca/crmp?passfile=.pgpass"
```

### Download Only
To only download files for later processing:

```bash
python scripts/bulk_download.py \
    -N ec \
    -d /tmp/downloads \
    -S "2025-01-01 00:00:00" \
    -E "2025-01-01 23:59:59" \
    -F hourly
```

### Process Only
To process previously downloaded files:

```bash
python scripts/bulk_process.py \
    -d /tmp/downloads \
    -N ec \
    -c "dbname=rtcrmp user=crmp"
```

---

## 1. Bulk Download (`bulk_download.py`)

Downloads data files for specified time ranges and networks. Files are saved with timestamped filenames for later processing.

### Basic Usage

```bash
python scripts/bulk_download.py \
    -N <network> \
    -d <directory> \
    -S "2025-01-01 00:00:00" \
    -E "2025-01-02 00:00:00" \
    -F hourly
```

### Essential Parameters

- `-N, --network`: Network name (required) - see [Available Networks](#available-networks)
- `-d, --directory`: Directory to save downloaded files (default: `~/bulk_download`)
- `-S, --start_date`: Start time in "YYYY-MM-DD HH:MM:SS" format (required)
- `-E, --end_date`: End time in "YYYY-MM-DD HH:MM:SS" format (defaults to current time)
- `-F, --frequency`: Download frequency - "hourly" or "daily" (required)

### Logging Options

- `--log_conf`: Path to logging configuration file
- `--log_filename`: Log file path (default: `/tmp/crmp/download_main.txt`)
- `--log_level`: Log level (default: INFO)
- `--error_email`: Email for error notifications (default: `pcic.devops@uvic.ca`)

### Examples

#### Download hourly EC data for bc
```bash
python scripts/bulk_download.py \
    -N ec \
    -d /workspaces/crmprtd/infill-cache \
    -S "2025-01-26 00:00:00" \
    -E "2025-01-27 00:00:00" \
    -F hourly
```

#### Download daily data with custom logging
```bash
python scripts/bulk_download.py \
    -N bc_hydro \
    -d /tmp/hydro_data \
    -S "2025-01-01 00:00:00" \
    -E "2025-01-31 00:00:00" \
    -F daily \
    --log_filename /tmp/bulk_download.log \
    --log_level DEBUG
```

### Output Files

Files are saved with the naming convention:
```
{network}_{timestamp}_{frequency}.xml
```

Example: `ec_2025-01-26 12-00-00_hourly.xml`

---

## 2. Bulk Process (`bulk_process.py`)

Processes multiple downloaded files using the `crmprtd.process` pipeline. Designed to work with files from `bulk_download.py` or other download scripts.

### Basic Usage

```bash
python scripts/bulk_process.py \
    -d <directory> \
    -N <network> \
    -c "dbname=rtcrmp user=crmp"
```

### Essential Parameters

- `-N, --network`: Network type (required) - see [Available Networks](#available-networks)
- `-c, --connection_string`: PostgreSQL connection string (required)
- `-S, --start_date`: Start time in "YYYY-MM-DD HH:MM:SS" format (required)
- `-E, --end_date`: End time in "YYYY-MM-DD HH:MM:SS" format (optional)

### File Selection (choose one)

- `-d, --directory`: Directory containing files to process
- `-p, --pattern`: File pattern to match (e.g., `"crmprtd_download_2025-01-*.xml"`)

### Processing Options

- `--continue-on-error`: Continue processing if one file fails
- `--move-processed`: Move successfully processed files to 'processed' subdirectory

### Database Options

- `-R, --insert_strategy`: Strategy for inserting data (BULK, SINGLE, CHUNK_BISECT, ADAPTIVE)
- `-C, --bulk_chunk_size`: Chunk size for BULK strategy (default: 1000)
- `--sample_size`: Sample size for duplicate detection (default: 50)

### Examples

#### Process all files in a directory
```bash
python scripts/bulk_process.py \
    -d /workspaces/crmprtd/infill-cache \
    -N ec \
    -c "dbname=rtcrmp user=crmp" \
    --continue-on-error \
    --move-processed
```

#### Process specific date range in diagnostic mode
```bash
python scripts/bulk_process.py \
    -d /workspaces/crmprtd/infill-cache \
    -p "ec_2025-01-*.xml" \
    -N ec \
    -c "dbname=rtcrmp user=crmp" \
    -S "2025-01-01" \
    -E "2025-01-31" \
    -D
```

#### Process single file with inference
```bash
python scripts/bulk_process.py \
    -f /path/to/specific/file.xml \
    -N bc_hydro \
    -c "dbname=rtcrmp user=crmp" \
    -I
```

### File Management

- Use `--move-processed` to automatically move successfully processed files to a 'processed' subdirectory
- This helps avoid reprocessing the same files
- Failed files remain in the original location for retry

---

## 3. Bulk Pipeline (`bulk_pipeline.py`)

Orchestrates complete download-and-process operations using the `download_cache_process` functions. Provides a unified interface for running the complete pipeline for a single network across time ranges.

### Basic Usage

```bash
python scripts/bulk_pipeline.py \
    -N <network> \
    -S "2025-01-01 00:00:00" \
    -E "2025-01-02 00:00:00" \
    -F hourly \
    -c "dbname=rtcrmp user=crmp"
```

### Essential Parameters

- `-N, --network`: Network name or alias (required) - see [Network Aliases](#network-aliases)
- `-S, --start_date`: Start time in "YYYY-MM-DD HH:MM:SS" format (required)
- `-c, --connection_string`: Database connection string for processing

### Time Range Options

- `-E, --end_date`: End time in "YYYY-MM-DD HH:MM:SS" format (defaults to current time)

### Cache and Processing Options

- `--cache-directory`: Directory to store cache files
- `--dry-run`: Print commands without executing them
- `--tag`: Tag to include in cache and log filenames

### EC Network Specific

- `-p, --province`: Province code(s) for EC network (can be used multiple times)

### Control Options

- `--force`: Continue processing if individual operations fail
- `--delay`: Delay in seconds between operations (default: 3)

### Information

- `--list-networks`: List available networks and aliases, then exit

### Examples

#### Process EC data for British Columbia
```bash
python scripts/bulk_pipeline.py \
    -N ec \
    -p BC \
    -S "2025-01-26 00:00:00" \
    -E "2025-01-27 00:00:00" \
    -F hourly \
    -c "dbname=rtcrmp user=crmp" \
    --cache-directory /tmp/ec_cache
```

#### Process single time point with custom tag
```bash
python scripts/bulk_pipeline.py \
    -N hourly_swobml2 \
    -S "2025-07-28 18:00:00" \
    -E "2025-07-28 18:00:00" \
    -F hourly \
    -c "dbname=rtcrmp user=crmp" \
    --cache-directory /workspaces/crmprtd/cache \
    --tag "manual_run"
```

#### Dry run to preview operations
```bash
python scripts/bulk_pipeline.py \
    -N bc_hydro \
    -S "2025-07-28 12:00:00" \
    -F hourly \
    --dry-run \
    -c "dbname=rtcrmp user=crmp"
```

---

## Available Networks

The following networks are supported across all bulk scripts:

### Primary Networks
- `ec`: Environment and Climate Change Canada
- `bc_hydro`: BC Hydro
- `crd`: Capital Regional District
- `moti`: Ministry of Transportation and Infrastructure
- `wamr`: Weather stations
- `wmb`: Water Management Branch

### SWOB Partner Networks
- `bc_env_aq`: BC Environment Air Quality
- `bc_env_snow`: BC Environment Snow
- `bc_forestry`: BC Forestry
- `bc_riotinto`: BC Rio Tinto
- `bc_tran`: BC Transportation
- `nt_forestry`: NT Forestry
- `nt_water`: NT Water
- `yt_gov`: Yukon Government
- `yt_water`: Yukon Water
- `yt_firewx`: Yukon Fire Weather
- `yt_avalanche`: Yukon Avalanche
- `dfo_ccg_lighthouse`: DFO CCG Lighthouse

### Test Network
- `_test`: Test network for development

## Network Aliases

The `bulk_pipeline.py` script supports network aliases for common groupings:

- `bch`: bc_hydro
- `hourly_swobml2`: bc_env_snow, bc_forestry, bc_riotinto, bc_tran, dfo_ccg_lighthouse
- `ytnt`: nt_forestry, nt_water, yt_gov, yt_water, yt_avalanche, yt_firewx

### Using Network Aliases

```bash
# Process all networks in the hourly_swobml2 group
python scripts/bulk_pipeline.py \
    -N hourly_swobml2 \
    -S "2025-07-28 00:00:00" \
    -F hourly \
    -c "dbname=rtcrmp user=crmp"
```

---

## Common Workflows

### 1. Download-Process Workflow (Separate Steps)

For maximum control, download and process in separate steps:

```bash
# Step 1: Download files
python scripts/bulk_download.py \
    -N ec \
    -d /tmp/ec_data \
    -S "2025-01-01 00:00:00" \
    -E "2025-01-31 23:59:59" \
    -F daily

# Step 2: Process downloaded files
python scripts/bulk_process.py \
    -d /tmp/ec_data \
    -N ec \
    -c "dbname=rtcrmp user=crmp" \
    --continue-on-error \
    --move-processed
```

### 2. Pipeline Workflow (Single Step)

For streamlined operations, use the pipeline:

```bash
python scripts/bulk_pipeline.py \
    -N ec \
    -p BC \
    -S "2025-01-01 00:00:00" \
    -E "2025-01-31 23:59:59" \
    -F daily \
    -c "dbname=rtcrmp user=crmp"
```

### 3. Multi-Network Processing

For multiple networks, run the pipeline script multiple times:

```bash
for network in bc_hydro bc_env_snow bc_forestry; do
    python scripts/bulk_pipeline.py \
        -N $network \
        -S "2025-07-28 00:00:00" \
        -E "2025-07-28 06:00:00" \
        -F hourly \
        -c "dbname=rtcrmp user=crmp" \
        --force \
        --delay 5
done
```

### 4. Error Recovery

If processing fails partway through:

```bash
# First, try diagnostic mode to identify issues
python scripts/bulk_process.py \
    -d /path/to/files \
    -N ec \
    -c "dbname=rtcrmp user=crmp" \
    -D

# Then process with error handling
python scripts/bulk_process.py \
    -d /path/to/files \
    -N ec \
    -c "dbname=rtcrmp user=crmp" \
    --continue-on-error \
    --move-processed
```

---

## Logging

All scripts support comprehensive logging:

### Default Locations
- `bulk_download.py`: `/tmp/crmp/download_main.txt`
- `bulk_process.py`: Uses crmprtd logging configuration
- `bulk_pipeline.py`: `/tmp/crmp/bulk_pipeline.log`

### Custom Logging
```bash
python scripts/bulk_pipeline.py \
    -N bc_hydro \
    --log_filename /custom/path/pipeline.log \
    --log_level DEBUG \
    -c "dbname=rtcrmp user=crmp"
```

### Logging Levels
- `DEBUG`: Detailed information for troubleshooting
- `INFO`: General information about script progress (default)
- `WARNING`: Warning messages about potential issues
- `ERROR`: Error messages about failures

---

## Performance Tips

1. **Use appropriate chunk sizes**: For large datasets, adjust `--bulk_chunk_size` in bulk_process.py
2. **Add delays**: Use `--delay` in bulk_pipeline.py to avoid overwhelming servers
3. **Process in smaller batches**: Break large time ranges into smaller chunks
4. **Use diagnostic mode**: Test with `-D` flag before full processing
5. **Monitor disk space**: Ensure adequate space for downloads and processing
6. **Use move-processed**: Automatically organize processed files to avoid reprocessing

---

## Troubleshooting

### Common Issues

1. **Connection errors**: Check database connection string and network access
2. **File permissions**: Ensure write access to cache and log directories

### Getting Help

- Use `--list-networks` to see available networks
- Use `--dry-run` to preview operations without execution
- Use `-D` diagnostic mode to test without database commits
- Check log files for detailed error information

### Example Diagnostic Commands

```bash
# List available networks
python scripts/bulk_pipeline.py --list-networks

# Test download without processing
python scripts/bulk_download.py -N ec -d /tmp/test -S "2025-01-01 12:00:00" -E "2025-01-01 12:00:00" -F hourly

# Test processing in diagnostic mode
python scripts/bulk_process.py -f /tmp/test/ec_*.xml -N ec -c "dbname=rtcrmp user=crmp" -D
```
