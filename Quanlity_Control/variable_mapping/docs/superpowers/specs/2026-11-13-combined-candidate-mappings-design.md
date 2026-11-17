# Combined Candidate Mappings Design

## Intent

Provide one reproducible CSV containing every saved network candidate mapping for cross-network review.

## Selected approach

Create a reusable, commented notebook at `3.combine_candidate_mappings.ipynb`. It discovers each network-prefixed candidate CSV, loads it through the existing schema-normalizing loader, validates that its rows match the network folder and filename, concatenates all rows, enriches each `vars_id` from the database `meta_vars` table, and atomically replaces one combined CSV. Editable settings appear near the top, the validation logic remains independently tested, and the final cell displays only the latest run result.

The earlier standalone `.py` command is removed so there is only one implementation to maintain.

## Output

The default output is `networks/all_networks_candidate_mappings.csv`. It contains, in order: `network_id`, `canonical_variable`, `vars_id`, `net_var_name`, `standard_name`, `cell_method`, `long_description`, `display_name`, `network_station_count`, `source_time_scale`, and `daily_aggregation`. The four descriptive metadata fields come from `meta_vars`. It intentionally omits `priority`, `source_family`, and `mapping_status`. Source files remain unchanged.

## Validation

Reject a source whose folder ID, filename ID, or row `network_id` values disagree. Reject duplicate `(network_id, vars_id, canonical_variable)` rows, duplicate `meta_vars` rows, missing `meta_vars` rows, and candidate/metadata network mismatches. Sort by network, canonical variable, variable ID, and name. Fail clearly when no source files exist. The database URL is supplied with `--db-url` or `CRMP_DB_URL`.
