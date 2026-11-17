# Persistent Candidate Exclusions Design

## Intent

Keep rejected variables visible as reviewed candidates while guaranteeing that they are not queried, plotted, or selected as final sources. Carry the exclusion decision into final rules for auditability and future runs.

## Approved behavior

- Discovery `EXCLUDE` entries remain in `candidate_mappings.csv` with `mapping_status = excluded` instead of being deleted.
- Manual candidate overrides take precedence over exclusions and may restore/reclassify an ID as `mapping_status = candidate`.
- Batch review separates active and excluded rows by canonical variable. Only active rows participate in station selection, recent-data checks, plots, and automatic keeps.
- Every generated rule stores excluded IDs as JSON in `excluded_source_vars_ids`.
- Final-rule column order is `source_vars_ids`, `excluded_source_vars_ids`, `recent_source_vars_ids`, `recent_source_latest_observations`, followed by the remaining metadata.
- Network 19 candidate `837` remains visible as an excluded precipitation candidate. Its current final rule becomes `source_vars_ids = [546]` and `excluded_source_vars_ids = [837]`; it is also removed from recent-source fields.

## Approaches considered

- Delete excluded candidate rows: simple, but loses the reviewed decision and discovery can recreate the candidate.
- Keep a separate exclusion list only in the review notebook: works, but creates a second source of truth.
- **Candidate row with excluded status — selected:** one persistent source of truth that flows automatically into final rules.

## Constraints

- Existing active candidate behavior is unchanged.
- Excluded rows remain valid candidate-registry records and retain name, aggregation, priority, and source-family metadata.
- Existing final-rule files without the new column remain readable and receive an empty exclusion list when next saved.
- Current Network 19 CSVs are updated consistently without rewriting unrelated review evidence files.
