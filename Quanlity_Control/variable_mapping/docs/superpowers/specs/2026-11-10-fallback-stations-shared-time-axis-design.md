# Fallback Stations and Shared Time Axis Design

## Intent

Make batch review useful when no station contains every candidate for a canonical variable, and make time-series pages visually comparable across stations.

## Root cause

The current batch runner selects only stations containing every candidate ID. Network 5 air temperature has five candidates, including radiation false positives `675` (`L_down_corr_Avg`) and `677` (`L_up_corr_Avg`), while precipitation has six products with different accumulation periods. No station contains every candidate in either group, so both reviews stop with `no_matching_stations`.

## Approved behavior

1. Keep the strict all-candidate station search as the preferred method.
2. If it returns no stations, automatically select stations containing at least one candidate.
3. Record `all_candidates` or `any_candidate_fallback` in `run_summary.csv` so the sampling basis is explicit.
4. Continue recent-data checks across every candidate and sampled fallback station; a missing candidate at a station remains a missing observation, not an error.
5. For each canonical variable, compute the earliest and latest plausible observation across all selected plot stations and apply that x-axis range to every station time-series page for that variable. ECDF behavior is unchanged.
6. Add Network 5 exclusions for candidate IDs `675` and `677`, and remove their current rows from `networks/network_5/candidate_mappings.csv`.

## Approaches considered

- Strict-only matching: preserves direct candidate comparison but produces no review for heterogeneous networks.
- Automatic any-candidate fallback — selected: preserves strict comparison when possible and still provides evidence when candidate coverage does not overlap.
- Separate report per candidate: maximizes coverage but fragments the canonical-variable review and makes comparisons harder.

## Constraints

- The fallback activates only when strict matching returns zero stations.
- Other networks and canonical variables retain current behavior when strict matches exist.
- Candidate IDs remain visible in legends, so station pages clearly show which sources are present.
- The current Network 5 `latest_review/` is not rewritten without a database rerun; the user reruns the batch notebook to generate updated reports.
