# Network-wide candidate station counts

## Intent

Make the number of stations carrying each candidate variable visible in both
candidate discovery and batch review outputs, without confusing it with the
sampled recent-data count.

## Behavior

- Add `network_station_count` to `net<N>_candidate_mappings.csv` for every
  candidate row, including excluded candidates.
- Add the same column to `latest_review/net<N>_candidate_review.csv` for active
  candidates reviewed and plotted by the batch notebook.
- Define the count as distinct stations in that network having at least one
  non-null `obs_raw` observation for the `vars_id` at any date.
- Keep `recent_non_null_station_count` unchanged: it continues to describe only
  the sampled source-check stations with data on or after the cutoff.
- Candidate discovery calculates and saves counts. Batch review reuses saved
  counts and calculates them as a backward-compatible fallback when an older
  candidate mapping file lacks the column.

## Approaches considered

1. Save only in candidate discovery. This is fastest for batch review but leaves
   the batch table incomplete and requires every older mapping file to be rerun.
2. Calculate only during batch review. This omits the requested discovery output.
3. Save during discovery and carry into batch review, with a fallback for legacy
   mappings. This is the selected approach because both requested files remain
   useful and existing networks continue to run.

## Constraints and non-goals

- Use the existing lightweight `summarize_variable_station_presence()` query.
- Do not change source selection, frequency classification, or `source_vars_ids`.
- Do not reinterpret the count as recent, plausible, or continuous coverage.
- Tests must distinguish the network-wide count from sampled recent counts and
  cover zero-observation and excluded candidates.
