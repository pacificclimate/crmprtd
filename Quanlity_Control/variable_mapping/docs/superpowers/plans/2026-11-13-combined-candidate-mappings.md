# Combined Candidate Mappings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable command that combines all network candidate registries into one reduced-column CSV enriched with descriptive `meta_vars` fields.

**Architecture:** Put combination and validation logic in a focused notebook under `scripts/`. Reuse `load_candidate_mappings` for legacy schema compatibility, query `meta_vars` once for all candidate IDs, and keep the function in tagged code cells that tests load directly.

**Tech Stack:** Python, pandas, SQLAlchemy, argparse, pytest

**Spec:** `docs/superpowers/specs/2026-11-13-combined-candidate-mappings-design.md`

## Global Constraints

- Do not modify individual network candidate files.
- Omit `priority`, `source_family`, and `mapping_status` only from the combined output.
- Default output: `networks/all_networks_candidate_mappings.csv`.
- Replace the output only after validation succeeds.

## Review Focus

- Legacy source files missing optional columns normalize successfully.
- Folder, filename, and row network IDs must agree.
- Duplicate candidate keys must fail rather than silently deduplicate.
- Every candidate `vars_id` must have exactly one `meta_vars` row for the same network.
- The output file must not be included as an input.
- Empty input directories must fail clearly.

---

### Task 1: Combine and validate candidate mappings

**Files:**
- Create: `scripts/combine_candidate_mappings.py`
- Create: `tests/test_combine_candidate_mappings.py`

**Interfaces:**
- Produces: `combine_candidate_mappings(networks_dir: Path, output_path: Path, engine: sa.Engine) -> pd.DataFrame`
- Produces: CLI options `--networks-dir`, `--output`, and `--db-url`

- [x] **Step 1: Write failing tests for column selection, deterministic order, validation, and empty input.**
- [x] **Step 2: Run focused tests and verify RED.**
- [x] **Step 3: Implement the callable function and CLI with atomic output replacement.**
- [x] **Step 4: Run focused tests and verify GREEN.**
- [x] **Step 5: Run the command on the real network folders and validate the combined CSV.**
- [x] **Step 6: Run the complete test suite and `git diff --check`.**

### Task 2: Enrich candidates with database metadata

**Files:**
- Modify: `scripts/combine_candidate_mappings.py`
- Modify: `tests/test_combine_candidate_mappings.py`

- [x] **Step 1: Write failing tests for metadata columns and missing metadata.**
- [x] **Step 2: Query `meta_vars`, validate the merge, and add the four metadata columns.**
- [x] **Step 3: Run focused tests and verify GREEN.**
- [x] **Step 4: Regenerate and independently validate the real combined CSV.**
- [x] **Step 5: Run the complete test suite and final repository checks.**

### Task 3: Convert the command to a documented notebook

**Files:**
- Create: `3.combine_candidate_mappings.ipynb`
- Delete: `scripts/combine_candidate_mappings.py`
- Modify: `tests/test_combine_candidate_mappings.py`

- [x] **Step 1: Change tests to load the notebook implementation and verify RED while it is absent.**
- [x] **Step 2: Add the commented notebook with editable settings, tested logic, and one run/preview cell.**
- [x] **Step 3: Run focused tests and verify GREEN.**
- [x] **Step 4: Remove the obsolete Python script and update documentation.**
- [x] **Step 5: Execute the notebook with `.venv` and run final verification.**
