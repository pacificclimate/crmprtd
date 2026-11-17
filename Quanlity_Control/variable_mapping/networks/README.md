# Network data folders

Use the shared notebooks in the repository root for every network. Do not copy the
notebooks into these folders.

`all_networks_source_vars_summary.csv` compares final sources across networks. It
classifies a saved source as latest-data automatic, sole-candidate automatic, or
manual. These three columns partition each row's final `source_vars_ids`.

## Run a network

1. Set `NETWORK_ID` in `0.candidate_discovery.ipynb` and run it to create
   `networks/network_<id>/net<id>_candidate_mappings.csv`.
2. Use `1.variable_decide.ipynb` for an optional single-variable review, or set the
   same `NETWORK_ID` in `2.all_variables_decide.ipynb` to review all variables.
3. The final selections are saved to `net<id>_final_variable_rules.csv` in that
   network's folder.

Both `net<id>_candidate_mappings.csv` and
`latest_review/net<id>_candidate_review.csv` include
`network_station_count`: the number of distinct stations in that network with at
least one non-null observation for the candidate at any date. The separate
`recent_non_null_station_count` in candidate review output counts only sampled
stations with data on or after the configured cutoff.

Candidate discovery saves `source_time_scale` as `daily` or `hourly` for active
candidates. A candidate with `network_station_count == 0` is automatically marked
`excluded` and leaves `source_time_scale` blank because it has no observations to
classify or plot. Active candidates use up to 300 timestamps from one source
history first, then stored frequency and variable metadata. Reporting cadence is
separate from aggregation interval: for example, a rolling 24-hour value stored
every hour is `hourly`. Add an entry to
`SOURCE_TIME_SCALE_OVERRIDES_BY_NETWORK` in the discovery notebook only when a
nonzero-station candidate remains unresolved. Time-series legends show the saved
frequency for every plotted candidate. The shared
`SOURCE_VARS_TIME_SCALES_BY_NETWORK` registry remains a fallback for older CSVs.

`daily_aggregation` is assigned after cadence detection. Every source already
reported daily uses `as_is`. Hourly and subdaily sources retain the operation
appropriate to their meaning: for example, temperature can use `mean`, `min`,
or `max`; interval precipitation can use `sum`; a running daily accumulation can
use `last`; a cumulative gauge can use `difference`; and a rolling previous-
24-hour value can use `fixed_hour_previous_day`.

## Folder contents

```text
network_<id>/
├── net<id>_candidate_mappings.csv       # Candidate variables for this network
├── net<id>_final_variable_rules.csv     # Saved canonical-variable selections
├── figures/                     # Single-variable plots, created when needed
└── latest_review/               # Latest successful all-variable batch review
    ├── net<id>_time_series.pdf
    ├── net<id>_cdf.pdf
    ├── net<id>_candidate_review.csv
    ├── net<id>_run_summary.csv
    └── net<id>_final_variable_rules.csv
```

Each successful batch run replaces only that network's `latest_review/`. A failed
run leaves the previous successful review intact, and other network folders are not
changed.
