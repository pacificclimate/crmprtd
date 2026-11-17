# Persistent Candidate Exclusions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve candidate exclusions as registry status and propagate them safely into final rules.

**Architecture:** Discovery marks matching candidates excluded. Batch review partitions mappings into active and excluded sets, operates only on active IDs, and serializes excluded IDs into each rule at the save boundary.

**Tech Stack:** Python, pandas, pytest, Jupyter Notebook JSON, CSV

**Spec:** `docs/superpowers/specs/2026-11-10-persistent-candidate-exclusions-design.md`

## Global Constraints

- Excluded candidates never enter station queries, plots, recent checks, or source selections.
- Excluded candidates remain visible in the candidate registry.
- Legacy final-rule CSVs remain compatible.
- Network 19 ID 837 is removed from selected and recent-source fields.

## Review Focus

- A canonical variable with active and excluded candidates reviews only active IDs.
- A canonical variable with every candidate excluded reports no active candidates without querying the database.
- Manual overrides of an excluded ID restore it as an active candidate.
- Saving over a legacy final-rule CSV adds the new column without losing unrelated network rows.
- Exclusion metadata cannot overlap `source_vars_ids`.

---

### Task 1: Discovery exclusion status

**Files:**
- Modify: `0.candidate_discovery.ipynb`
- Modify: `tests/test_candidate_discovery_notebook.py`

**Interfaces:**
- Consumes: `EXCLUDE` pairs and discovered candidates
- Produces: reviewed candidates with `mapping_status = excluded`

- [ ] Write a failing notebook-cell test proving exclusions remain as rows and manual overrides win.
- [ ] Run the focused test and confirm current row-dropping behavior fails.
- [ ] Replace row deletion with status assignment before manual overrides.
- [ ] Run the focused test and confirm it passes.

### Task 2: Batch exclusion propagation

**Files:**
- Modify: `func/func_variable_review.py`
- Modify: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: candidate rows with `mapping_status`
- Produces: active review results plus `excluded_source_vars_ids`

- [ ] Write failing tests proving excluded IDs never reach selection/observation calls and appear in rules.
- [ ] Run focused tests and confirm the current runner includes excluded IDs.
- [ ] Partition active/excluded rows and add exclusion serialization and column ordering.
- [ ] Run focused tests and confirm they pass.

### Task 3: Network 19 persistent data update

**Files:**
- Modify: `networks/network_19/candidate_mappings.csv`
- Modify: `networks/network_19/final_variable_rules.csv`
- Modify: `networks/network_19/latest_review/final_rules.csv`

**Interfaces:**
- Consumes: current Network 19 decisions
- Produces: persistent exclusion status and consistent final-rule files

- [ ] Mark candidate 837 excluded and add it to the discovery notebook's `EXCLUDE` set.
- [ ] Update both final-rule files to select/recently track only 546 and record 837 as excluded.
- [ ] Validate schemas, JSON fields, uniqueness, and non-overlap.
- [ ] Run the complete test suite, Python compilation, and notebook validation.
