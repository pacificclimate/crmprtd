# Bulk Process Script Usage

This script (`bulk_process.py`) processes multiple downloaded files using the `crmprtd.process` pipeline. It's designed to work with files previously downloaded by `bulk_download.py` or other download scripts.

## Basic Usage

### Process all XML files in a directory
```bash
python scripts/bulk_process.py -d /path/to/directory -N ec -c "dbname=rtcrmp user=crmp"
```

### Process files matching a specific pattern
```bash
python scripts/bulk_process.py -d /path/to/directory -p "crmprtd_download_2025-06-*.xml" -N ec -c "dbname=rtcrmp user=crmp"
```

### Process a single file
```bash
python scripts/bulk_process.py -f /path/to/file.xml -N ec -c "dbname=rtcrmp user=crmp"
```

### Process files from a list
Create a text file with one filename per line, then:
```bash
python scripts/bulk_process.py --file-list file_list.txt -N ec -c "dbname=rtcrmp user=crmp"
```

## Common Options

### Essential Parameters
- `-N, --network`: Network type (required) - one of: ec, bc_hydro, crd, moti, wamr, wmb, etc.
- `-c, --connection_string`: PostgreSQL connection string (required)

### File Selection (choose one)
- `-d, --directory`: Directory containing files to process
- `-f, --filename`: Single file to process  
- `--file-list`: Text file with list of files to process

### Processing Options
- `-S, --start_date`: Start date filter (e.g., "2025-06-01")
- `-E, --end_date`: End date filter (e.g., "2025-06-30")
- `-D, --diag`: Diagnostic mode (no database commits)
- `-I, --infer`: Run inference stage to determine metadata
- `--continue-on-error`: Continue processing if one file fails
- `--move-processed`: Move successfully processed files to 'processed' subdirectory

### Database Options
- `-R, --insert_strategy`: Strategy for inserting data (BULK, SINGLE, CHUNK_BISECT, ADAPTIVE)
- `-C, --bulk_chunk_size`: Chunk size for BULK strategy (default: 1000)
- `--sample_size`: Sample size for duplicate detection (default: 50)

## Examples

### Process Environment Canada (EC) files from infill-cache directory
```bash
python scripts/bulk_process.py \
    -d /workspaces/crmprtd/infill-cache \
    -N ec \
    -c "dbname=rtcrmp user=crmp" \
    --continue-on-error \
    --move-processed
```

### Process specific date range of files in diagnostic mode
```bash
python scripts/bulk_process.py \
    -d /workspaces/crmprtd/infill-cache \
    -p "crmprtd_download_2025-06-*.xml" \
    -N ec \
    -c "dbname=rtcrmp user=crmp" \
    -S "2025-06-01" \
    -E "2025-06-30" \
    -D
```

### Process files with custom logging
```bash
python scripts/bulk_process.py \
    -d /workspaces/crmprtd/infill-cache \
    -N ec \
    -c "dbname=rtcrmp user=crmp" \
    -l /tmp/bulk_process_custom.log \
    -e your_email@example.com \
    --log-level DEBUG
```

## Networks Available

Available network types (`-N` option):
- `ec`: Environment and Climate Change Canada
- `bc_hydro`: BC Hydro 
- `crd`: Capital Regional District
- `moti`: Ministry of Transportation and Infrastructure
- `wamr`: Weather stations
- `wmb`: Water Management Branch
- And others: `yt_avalanche`, `yt_water`, `yt_firewx`, `dfo_ccg_lighthouse`, etc.

## File Management

- Use `--move-processed` to automatically move successfully processed files to a 'processed' subdirectory
- This helps avoid reprocessing the same files
- Failed files remain in the original location for retry


## Integration with bulk_download.py

This script is designed to work with files downloaded by `bulk_download.py`:

1. First download files:
   ```bash
   python scripts/bulk_download.py --starttime "2025-06-01 00:00:00" --endtime "2025-06-30 23:59:59" -F daily
   ```

2. Then process them:
   ```bash
   python scripts/bulk_process.py -d /path/to/cache/directory -N ec -c "dbname=rtcrmp user=crmp"
   ```
