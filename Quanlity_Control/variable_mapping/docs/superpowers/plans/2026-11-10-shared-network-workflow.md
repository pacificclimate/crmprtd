# Shared Network Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize variable mapping into one reusable notebook workflow with isolated, stable input and output paths for each network.

**Architecture:** Generic notebooks derive `NETWORK_DIR` from `NETWORK_ID`. The shared batch runner stages a complete review and safely promotes it to the network's stable `latest_review/` directory only after success.

**Tech Stack:** Python, pandas, pathlib, pytest, Jupyter Notebook JSON

**Spec:** `docs/superpowers/specs/2026-11-10-shared-network-workflow-design.md`

## Global Constraints

- Preserve current Network 2 CSV and review contents during migration.
- Keep one shared copy of every notebook and function.
- Failed reviews must retain the prior `latest_review/` directory.
- Paths shown inside notebooks must be derived from `NETWORK_ID`.

## Review Focus

- Promotion failure does not destroy the previous successful review.
- Staging and backup paths do not remain after successful promotion.
- Running network 2 cannot alter a different network directory.
- Notebooks run from the `variable_mapping` directory and reference only network-local files.
- Migrated Network 2 artifacts retain their original bytes.

---

### Task 1: Stable latest-review promotion

**Files:**
- Modify: `func/func_variable_review.py`
- Modify: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: `run_variable_reviews(..., output_dir=<network directory>)`
- Produces: `<output_dir>/latest_review/` and `results['run_dir']` pointing to it

- [ ] Write failing tests for successful replacement, cross-network isolation, and failure preservation.
- [ ] Run the focused tests and confirm failures describe the timestamp-directory behavior.
- [ ] Implement staging, backup, promotion, rollback, and cleanup within the supplied network directory.
- [ ] Run focused tests and confirm they pass.

### Task 2: Reusable notebook paths

**Files:**
- Rename: `0.net2_candidate_discovery.ipynb` to `0.candidate_discovery.ipynb`
- Rename: `1.net2_variable_decide.ipynb` to `1.variable_decide.ipynb`
- Rename: `2.net2_all_variables_decide.ipynb` to `2.all_variables_decide.ipynb`

**Interfaces:**
- Consumes: `NETWORK_ID`
- Produces: `NETWORK_DIR`, stable CSV paths, network-local figure paths, and `latest_review/`

- [ ] Update all three notebooks to derive paths from `HERE / 'networks' / f'network_{NETWORK_ID}'`.
- [ ] Update explanatory text to describe the reusable workflow and stable per-network paths.
- [ ] Clear execution counts and stored outputs, then validate notebook JSON and path references.

### Task 3: Network 2 migration and verification

**Files:**
- Move: `outfile/0.net2_candidate_mappings.csv` to `networks/network_2/candidate_mappings.csv`
- Move: `outfile/1.net2_final_variable_rules.csv` to `networks/network_2/final_variable_rules.csv`
- Move: current batch review contents to `networks/network_2/latest_review/`

**Interfaces:**
- Consumes: existing Network 2 artifacts
- Produces: the approved per-network directory layout

- [ ] Record checksums of existing artifacts and move them to the new layout.
- [ ] Verify checksums are unchanged and legacy workflow paths contain no data artifacts.
- [ ] Run the complete test suite, Python compilation, and notebook validation.
