# Latest Network Review Design

## Intent

Keep only the latest successful batch-review results for each network, while ensuring the final rule CSV places recent-source metadata directly after the selected source IDs.

## Constraints

- Retention is independent per `network_id`; running one network must not remove another network's results.
- Existing results remain available if a new review fails.
- `final_rules.csv` and the cumulative final-rule file place `recent_source_vars_ids` and `recent_source_latest_observations` immediately after `source_vars_ids`.
- The notebook remains reusable for networks other than network 2 by changing `NETWORK_ID`.

## Approach

Continue creating a unique temporary run directory. After every output file has been written successfully, remove older run directories whose names belong to the same network. This is safer than deleting first and retains the existing timestamped output convention. Centralize final-rule column ordering in `save_review_rules`, so both CSV outputs share the same schema.

Alternatives considered were a fixed `network_<id>_latest` directory (simpler naming but risks mixing partial outputs on failure) and notebook-only cleanup (would not protect future callers of the shared function). The shared-function, post-success cleanup approach was selected.

## Non-goals

- Do not remove output folders for other networks.
- Do not change candidate selection, sampling, plotting, or rule-selection behavior.
- Do not preserve older same-network runs.
