# Latest Network Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retain only the latest successful batch-review directory per network and order recent-source fields immediately after `source_vars_ids` in saved rule CSVs.

**Architecture:** Add post-success, same-network directory cleanup to the shared batch runner. Add a single column-ordering helper at the rule-save boundary and refresh the notebook narrative and stored outputs to match current behavior.

**Tech Stack:** Python, pandas, pathlib, pytest, Jupyter Notebook JSON

**Spec:** `docs/superpowers/specs/2026-11-10-latest-network-review-design.md`

## Global Constraints

- Cleanup must occur only after successful output generation.
- Cleanup must affect only directories for the current `network_id`.
- Both final-rule CSVs must use the requested column adjacency.

## Review Focus

- A failed run leaves the previous successful run untouched.
- Network IDs with shared numeric prefixes, such as 2 and 20, remain isolated.
- Unrelated files and directories under `batch_reviews` remain untouched.
- Existing cumulative rules with legacy column orders are normalized on the next save.
- Empty rule updates preserve existing rules without destructive rewrites.

---

### Task 1: Per-network latest-run retention

**Files:**
- Modify: `func/func_variable_review.py`
- Test: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: `run_variable_reviews(..., output_dir, network_id=...)`
- Produces: one successful `network_<id>_*` directory per network

- [ ] Write tests proving a second successful run removes the prior same-network directory but retains another network's directory and unrelated content.
- [ ] Run the focused tests and confirm they fail for missing cleanup.
- [ ] Implement post-success cleanup using exact `network_<id>_` name matching.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Final-rule column order

**Files:**
- Modify: `func/func_variable_review.py`
- Test: `tests/test_variable_review.py`

**Interfaces:**
- Consumes: combined and run-specific rule data frames
- Produces: CSVs with `source_vars_ids`, `recent_source_vars_ids`, and `recent_source_latest_observations` adjacent in that order

- [ ] Write a test asserting both CSV schemas and the returned frame use the requested order.
- [ ] Run the focused test and confirm it fails with the current order.
- [ ] Implement shared column normalization at the save boundary.
- [ ] Run the focused test and confirm it passes.

### Task 3: Notebook alignment and full verification

**Files:**
- Modify: `2.net2_all_variables_decide.ipynb`

**Interfaces:**
- Consumes: shared review functions
- Produces: a clean notebook describing latest-per-network retention without stale execution output

- [ ] Update notebook explanations to describe latest-per-network retention and remove previous-run restoration guidance.
- [ ] Clear stored cell outputs and execution counts so only future latest-run results appear.
- [ ] Validate notebook JSON and run the complete pytest suite.
