# Precipitation Daily Processing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct precipitation daily-processing metadata for future discovery and all existing candidate CSV outputs without rerunning networks.

**Architecture:** Add one reusable classifier/enricher to `func_variable_mapping.py`, call it after cadence detection in candidate discovery, and make batch auto-selection respect its readiness status. Migrate saved CSVs mechanically from existing metadata.

**Tech Stack:** Python, pandas, pytest, Jupyter notebooks, CSV

**Spec:** `docs/superpowers/specs/2026-11-16-precipitation-daily-processing-design.md`

## Global Constraints

- Do not rerun discovery for every network.
- Do not change existing final `source_vars_ids`.
- Do not guess a timezone or day-boundary hour.
- Preserve excluded candidates and source files unrelated to mapping outputs.

## Review Focus

- Daily, interval, rolling-24-hour, running-daily, cumulative, and detector cases classify differently.
- Legacy candidate registries remain loadable.
- Unresolved daily processing is not automatically selected.
- Empty network registries retain the complete schema.
- Migration preserves row counts and candidate keys.

### Task 1: Add and test daily-processing classification

**Files:**
- Modify: `func/func_variable_mapping.py`
- Modify: `tests/test_variable_review.py`

- [x] **Step 1: Write classification and registry round-trip tests and verify RED.**
- [x] **Step 2: Implement the classifier, schema defaults, validation, and overrides.**
- [x] **Step 3: Run focused tests and verify GREEN.**

### Task 2: Use classification in discovery and review

**Files:**
- Modify: `0.candidate_discovery.ipynb`
- Modify: `func/func_variable_review.py`
- Modify: `tests/test_candidate_discovery_notebook.py`
- Modify: `tests/test_variable_review.py`

- [x] **Step 1: Write failing integration tests.**
- [x] **Step 2: Enrich candidates after cadence detection and filter automatic keeps by readiness.**
- [x] **Step 3: Run focused tests and verify GREEN.**

### Task 3: Migrate existing CSV outputs

**Files:**
- Modify: `networks/network_*/net*_candidate_mappings.csv`
- Modify: `networks/network_*/latest_review/net*_candidate_review.csv`
- Modify: `networks/all_networks_candidate_mappings.csv`
- Modify: `3.combine_candidate_mappings.ipynb`

- [x] **Step 1: Update the combined-notebook schema for the new columns.**
- [x] **Step 2: Apply the classifier to saved CSVs without database discovery.**
- [x] **Step 3: Validate counts, keys, classifications, and unchanged final source IDs.**
- [x] **Step 4: Run the full test suite and repository checks.**
