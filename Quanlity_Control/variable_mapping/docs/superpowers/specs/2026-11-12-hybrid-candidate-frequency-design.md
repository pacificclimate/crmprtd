# Hybrid candidate-frequency detection

## Intent

Determine `hourly` or `daily` during candidate discovery, save the result with
each candidate, and stop requiring a new hard-coded network entry before batch
review can run.

## Selected approach

Use hybrid detection:

1. For each unique candidate `vars_id`, inspect a small recent sample from one
   history containing non-null observations.
2. Classify sub-daily reporting as `hourly` and approximately daily reporting as
   `daily`. The classification describes how often values are reported, not the
   aggregation window represented by a value. Thus a rolling 24-hour amount
   updated every hour is `hourly`.
3. When observations are unavailable or cadence is inconclusive, use explicit
   metadata such as stored history frequency and unambiguous hourly/daily names
   or descriptions.
4. If neither source resolves the cadence, require a persistent reviewed override
   keyed by network and `vars_id`; never silently guess.

## Saved data and workflow

- Add `source_time_scale` to `net<N>_candidate_mappings.csv`, with values limited
  to `hourly` and `daily`.
- Candidate discovery calculates it for active and excluded candidate rows before
  saving.
- `2.all_variables_decide.ipynb` builds its plotting/final-rule frequency map from
  `source_time_scale` in the candidate registry.
- Keep the existing central frequency registry temporarily as a compatibility
  fallback for older candidate CSVs. New networks and newly rerun discovery files
  use their saved column and do not require a registry edit.
- Existing `source_vars_time_scales` in final rules remains unchanged in meaning.

## Detection boundaries

- Sample at most 300 timestamps from one history per unique candidate.
- Median/dominant gaps up to six hours classify as `hourly`; gaps from 18 through
  30 hours classify as `daily`.
- Cadence outside those bands is unresolved unless metadata or an override settles
  it.
- A candidate with no observations may use an override or unambiguous metadata;
  otherwise discovery raises an error naming the unresolved IDs.

## Persistent overrides

Store reviewed exceptions by network in candidate discovery, beside the existing
candidate exclusions and manual candidate mappings. Validate that every override
uses `hourly` or `daily` and belongs to the selected network's candidate set.

## Approaches considered

- Metadata only was rejected because aggregation windows do not equal reporting
  frequency.
- Full-history cadence analysis was rejected because it is unnecessarily slow.
- Hybrid sampling with reviewed exceptions was selected because it is fast,
  evidence-based, and auditable.

## Non-goals

- Do not infer monthly climatology or other unsupported cadences as hourly/daily.
- Do not change canonical aggregation, source selection, station counts, or final
  `source_vars_ids`.
