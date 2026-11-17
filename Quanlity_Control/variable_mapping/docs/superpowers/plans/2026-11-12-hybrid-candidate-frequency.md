# Hybrid Candidate Frequency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Infer and save each candidate's hourly/daily reporting frequency during discovery, then make batch review consume that saved value before any legacy fallback.

**Architecture:** Put cadence classification and database sampling in `func_variable_mapping.py`; candidate discovery supplies metadata and reviewed overrides, then saves `source_time_scale`. Batch review resolves a per-ID map from the candidate CSV and uses the existing central registry only for legacy files without the column.

**Tech Stack:** Python, pandas, SQLAlchemy, Jupyter notebooks, pytest

**Spec:** `docs/superpowers/specs/2026-11-12-hybrid-candidate-frequency-design.md`

## Global Constraints

- Reporting cadence is distinct from aggregation interval; hourly-updated rolling 24-hour values are `hourly`.
- Timestamp sampling is capped at 300 rows from one history per unique candidate.
- Gaps up to 6 hours are `hourly`; gaps from 18 through 30 hours are `daily`; other gaps require metadata or an override.
- Only `hourly` and `daily` are valid saved values.
- Unresolved candidates raise an error naming their IDs; never silently guess.
- Preserve station counts, canonical aggregation, final rules, and `source_vars_ids`.
- Do not commit the dirty shared worktree; the user did not request a commit.

## Review Focus

- A rolling 24-hour variable sampled hourly must classify as hourly.
- Missing or one-point observations must use metadata/override rather than a fabricated cadence.
- Explicit overrides must win and reject invalid values or IDs outside the candidate set.
- Legacy candidate CSVs without `source_time_scale` must still run through the central fallback.
- New candidate CSV values must override conflicting legacy registry values.

---

### Task 1: Cadence classification, sampling, and schema

**Files:**
- Modify: `func/func_variable_mapping.py`
- Test: `tests/test_variable_review.py`

**Interfaces:**
- Produces: `classify_source_time_scale(timestamps, metadata_text, history_frequency) -> str | None`
- Produces: `add_candidate_time_scales(engine, mappings, metadata, network_id, overrides=None, sample_size=300) -> pd.DataFrame`
- Extends: candidate registry with optional legacy-compatible `source_time_scale`

- [x] **Step 1: Write failing unit tests**

Test literal hourly, daily, sub-hourly, rolling-24-hour hourly, explicit metadata fallback, unresolved cadence, valid override, invalid override value, and override ID outside the candidate set. Test legacy load and saved-column preservation.

- [x] **Step 2: Run focused tests and verify RED**

Run: `python -m pytest -q tests/test_variable_review.py -k 'source_time_scale or candidate_time_scale'`

Expected: FAIL because the classifier/enrichment interfaces do not exist.

- [x] **Step 3: Implement minimal classifier, sampler, enrichment, and schema compatibility**

Use median positive timestamp gaps first, then stored history frequency, then unambiguous metadata. Apply reviewed overrides last and raise with unresolved IDs.

- [x] **Step 4: Run focused tests and verify GREEN**

Run the focused command from Step 2; expected PASS.

### Task 2: Discovery and batch integration

**Files:**
- Modify: `0.candidate_discovery.ipynb`
- Modify: `2.all_variables_decide.ipynb`
- Modify: `func/func_variable_review.py`
- Modify: `networks/README.md`
- Test: `tests/test_candidate_discovery_notebook.py`
- Test: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: `add_candidate_time_scales(...)` from Task 1
- Produces: `candidate_source_time_scales(candidate_mappings, network_id) -> dict[int, str]`

- [x] **Step 1: Write failing integration tests**

Test discovery saves active and excluded candidates with `source_time_scale`; test batch resolution prefers saved values, falls back for legacy files, and errors only when neither source covers an active ID.

- [x] **Step 2: Run focused tests and verify RED**

Run: `python -m pytest -q tests/test_candidate_discovery_notebook.py tests/test_variable_review.py -k 'source_time_scale or candidate_time_scale'`

Expected: FAIL because notebooks and batch resolution are not integrated.

- [x] **Step 3: Integrate discovery, persistent overrides, and batch resolution**

Add network-safe override configuration to discovery, call enrichment before saving, and have the batch notebook derive its map from the loaded candidate registry through the resolver.

- [x] **Step 4: Refresh network 12 and verify everything**

Populate `source_time_scale=hourly` for network 12 through the implemented inference path, clear failed notebook outputs, parse notebook code cells, run the full test suite, validate the CSV, and run `git diff --check`.

Expected: network 12 runs without the missing-label error; all tests pass; saved candidate values are complete and valid.
