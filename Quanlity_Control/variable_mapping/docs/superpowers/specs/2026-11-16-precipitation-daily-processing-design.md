# Precipitation Daily Processing Design

## Intent

Replace the blanket `daily_aggregation = sum` assignment with source-aware daily-processing metadata. Preserve scientifically clear cases, and mark timezone/day-boundary-dependent cases for review rather than guessing.

## Selected approach

Classify precipitation candidates from reporting cadence plus `net_var_name`, `standard_name`, `cell_method`, `display_name`, `short_name`, and `long_description`.

- Already-daily sources: `as_is` and ready.
- Non-overlapping interval amounts: `sum`; hourly day boundary remains unknown and needs review.
- Rolling previous-24-hour sources: `fixed_hour_previous_day`; boundary hour/time basis remain unknown and need review.
- Running daily accumulations: `last`; boundary remains unknown and needs review.
- Cumulative gauge totals: `difference`; reset/day boundary remain unknown and need review.
- Detector ratios/status variables: `not_applicable`, excluded.

Store `daily_boundary_hour`, `daily_time_basis`, and `daily_processing_status` beside `daily_aggregation`. Network-specific reviewed overrides may resolve unknown values. The review workflow must not automatically keep a source whose daily processing still needs review, including the sole-candidate fallback. Explicit manual selection remains possible after human review.

## Existing outputs

Update existing `net<N>_candidate_mappings.csv`, `latest_review/net<N>_candidate_review.csv`, and `all_networks_candidate_mappings.csv` files in place from their saved cadence and combined `meta_vars` metadata. Do not rerun database discovery or overwrite final-variable rules.

## Compatibility and validation

Legacy registries without the new columns remain readable. New saves always retain the new fields. Validate allowed operations/statuses, boundary hours, row counts, candidate keys, and unchanged final `source_vars_ids`.
