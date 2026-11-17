# Fallback Stations and Shared Time Axis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add transparent any-candidate station fallback and consistent per-variable time axes to batch review.

**Architecture:** Extend station selection with an explicit match mode, while the batch runner tries strict matching first and fallback matching only after an empty strict result. Compute one time range per canonical variable before rendering its station pages.

**Tech Stack:** Python, SQLAlchemy, pandas, matplotlib, pytest, CSV, Jupyter Notebook JSON

**Spec:** `docs/superpowers/specs/2026-11-10-fallback-stations-shared-time-axis-design.md`

## Global Constraints

- Strict all-candidate selection remains the default.
- Fallback selection requires at least one candidate at a station.
- Every station page for one canonical variable uses the same full time range.
- Network 5 candidate rows `675` and `677` are removed without changing other rows.

## Review Focus

- Empty strict selection triggers exactly one fallback query.
- Nonempty strict selection never triggers fallback.
- Fallback station samples can contain different candidate subsets without breaking recent checks or plots.
- A one-timestamp variable receives a valid nonzero x-axis range.
- Missing or null timestamps do not create an invalid shared range.

---

### Task 1: Any-candidate fallback

**Files:**
- Modify: `func/func_variable_mapping.py`
- Modify: `func/func_variable_review.py`
- Test: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: `select_candidate_stations(..., match='all'|'any')`
- Produces: batch status field `station_selection_method`

- [ ] Write failing tests for strict success, fallback activation, and invalid match mode.
- [ ] Run focused tests and confirm the failures identify the missing match mode and fallback.
- [ ] Implement the SQL selection modes and strict-then-fallback runner flow.
- [ ] Run focused tests and confirm they pass.

### Task 2: Shared per-variable time axis

**Files:**
- Modify: `func/func_variable_review.py`
- Test: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: plausible observations for all selected stations of one variable
- Produces: identical time-series x-limits on every station page

- [ ] Write a failing plot test that captures time-series x-limits for multiple stations.
- [ ] Run it and confirm current station-specific autoscaling fails the equality assertion.
- [ ] Compute and apply the shared range, expanding a single timestamp safely.
- [ ] Run focused tests and confirm they pass.

### Task 3: Network 5 candidate cleanup and notebook guidance

**Files:**
- Modify: `0.candidate_discovery.ipynb`
- Modify: `2.all_variables_decide.ipynb`
- Modify: `networks/network_5/candidate_mappings.csv`

**Interfaces:**
- Consumes: reviewed Network 5 candidate set
- Produces: rerunnable discovery exclusions and current clean candidate registry

- [ ] Add exclusions `(675, 'air_temperature')` and `(677, 'air_temperature')`.
- [ ] Remove only the corresponding CSV rows and validate row count, uniqueness, and schema.
- [ ] Explain fallback method in the batch notebook and clear stored outputs.
- [ ] Run the full test suite, Python compilation, notebook validation, and CSV integrity checks.
