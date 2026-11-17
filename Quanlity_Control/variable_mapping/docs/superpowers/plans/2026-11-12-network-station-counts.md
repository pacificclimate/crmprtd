# Network-wide Candidate Station Counts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Save an unambiguous network-wide station count for every candidate in discovery output and every active candidate in batch review output.

**Architecture:** Add one reusable enrichment helper around the existing lightweight station-presence query. Candidate discovery enriches all reviewed mappings before saving; batch review carries saved counts and uses the helper only as a backward-compatible fallback for legacy mappings.

**Tech Stack:** Python, pandas, SQLAlchemy, Jupyter notebooks, pytest

**Spec:** `docs/superpowers/specs/2026-11-12-network-station-counts-design.md`

## Global Constraints

- `network_station_count` means distinct stations in the selected network with at least one non-null `obs_raw` value for that `vars_id` at any date.
- Preserve `recent_non_null_station_count` as a sampled post-cutoff count.
- Include excluded candidates in discovery output; batch review continues to contain active candidates only.
- Do not change frequency classifications, source selection, or `source_vars_ids`.
- Do not commit the dirty shared worktree; the user did not request a commit.

## Review Focus

- Candidate with no observations receives integer zero rather than a missing value.
- Excluded discovery candidates retain their count.
- An old candidate mapping without the new column is enriched during batch review.
- A current mapping with complete counts does not issue another network-wide count query.
- Sampled recent counts remain separate and unchanged.

---

### Task 1: Reusable count enrichment and registry compatibility

**Files:**
- Modify: `func/func_variable_mapping.py`
- Test: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: `summarize_variable_station_presence(engine, vars_ids, network_id)`
- Produces: `add_network_station_counts(engine, mappings, network_id) -> pd.DataFrame`

- [ ] **Step 1: Write failing tests**

Add tests proving the helper assigns literal counts, fills an absent result with zero, preserves excluded rows, and that candidate registry load/save accepts the new optional column while remaining compatible with legacy files.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python -m pytest -q tests/test_variable_review.py -k 'network_station_count'`

Expected: FAIL because the helper and persisted column do not exist.

- [ ] **Step 3: Implement the helper and compatible registry schema**

Add `network_station_count` to saved mapping columns, fill it with nullable values when loading legacy registries, and implement one merge that returns integer zero for requested IDs absent from the query result.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python -m pytest -q tests/test_variable_review.py -k 'network_station_count'`

Expected: PASS.

### Task 2: Discovery and batch output integration

**Files:**
- Modify: `0.candidate_discovery.ipynb`
- Modify: `func/func_variable_review.py`
- Modify: `2.all_variables_decide.ipynb`
- Modify: `networks/README.md`
- Test: `tests/test_candidate_discovery_notebook.py`
- Test: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: `add_network_station_counts(engine, mappings, network_id)` from Task 1
- Produces: `network_station_count` in `net<N>_candidate_mappings.csv` and `latest_review/net<N>_candidate_review.csv`

- [ ] **Step 1: Write failing integration tests**

Test that the discovery final cell enriches all rows before saving, that batch review preserves a complete saved count without querying again, and that a legacy mapping is enriched once before review output is written.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python -m pytest -q tests/test_candidate_discovery_notebook.py tests/test_variable_review.py -k 'network_station_count'`

Expected: FAIL because neither workflow integrates the helper.

- [ ] **Step 3: Integrate both workflows**

Candidate discovery calls the helper before `save_candidate_mappings`. Batch review calls it only when the column is absent or contains missing values, then includes the column in candidate review CSV output. Update notebook/readme text to define both count columns.

- [ ] **Step 4: Verify notebooks and full suite**

Run: clear notebook outputs, parse every code cell, run `python -m pytest -q tests`, and run `git diff --check` on touched files.

Expected: notebook syntax valid; all tests pass; no whitespace errors.
