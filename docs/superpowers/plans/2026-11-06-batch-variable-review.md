# Batch variable review implementation plan

**Goal:** Run all six canonical-variable reviews once, then edit manual source IDs and save without repeating queries or plots.
**Architecture:** A shared Python module handles candidate loading, eligible-station sampling, recent-observation checks, plots, readouts, and rule saving. The notebook provides settings, one batch call, manual choices, and one save call.
**Constraints:** Preserve 20 jointly eligible source stations, independent plot sample, inclusive 2026 cutoff, compact rule schema, single check timestamp, existing rules for other variables. Produce two multipage PDFs per unique run folder.

- [x] Test batch behavior with synthetic data and mocked database boundaries: all six variables, two PDFs, saved readouts, sample restrictions, no eligible stations, empty cleaned data, manual validation, rules merge, and saving without queries.
- [x] Implement `run_variable_reviews` and `save_review_rules` in `Quanlity_Control/variable_mapping/func/func_variable_review.py` using existing query/QC helpers. Save review metadata JSON to allow reopening results.
- [x] Add a separate batch notebook alongside the existing single-variable notebook with documented batch settings, a single batch invocation, editable per-variable manual IDs, and independent save call.
- [x] Run tests, compile all notebook cells, and inspect output PDF page counts and saved schema. No production database calls during verification.

User clarification: preserve `1.net2_variable_decide.ipynb` unchanged during this batch addition. New entry point: `2.net2_all_variables_decide.ipynb`.

Verification: five synthetic integration tests cover all six variables, PDF page counts, sample limits, missing data, independent saving, invalid manual IDs, existing-rule preservation, and JSON/CSV readouts. Notebook code cells parse. Production database not queried. Independent review found no important issues; clarified save-cell messages for empty selections.
