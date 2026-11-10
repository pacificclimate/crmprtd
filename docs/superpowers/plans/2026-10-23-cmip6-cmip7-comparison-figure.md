# CMIP6–CMIP7 Comparison Figure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the separate plotting sections with one executed, self-contained 2 x 2 comparison figure using matched x- and y-axes.

**Architecture:** One notebook loads the CMIP6 IAM CSV and CMIP7 cached FaIR NetCDF, validates each schema, calculates the two distinct uncertainty treatments, and renders a shared-axis matplotlib grid. No CMIP6 data are extrapolated past 2100.

**Tech Stack:** Python, pandas, NumPy, xarray, matplotlib, Jupyter nbconvert

**Spec:** `docs/superpowers/specs/2026-10-23-cmip6-cmip7-comparison-figure.md`

## Global Constraints

- Python/matplotlib only for drawing, export, and QA.
- All panels use x-limits 2000–2150.
- Emissions panels use y-limits -50–100 Gt CO2-eq yr-1.
- Temperature panels use y-limits 0–5 °C/K above 1850–1900.
- CMIP6 stops at 2100 and is never extrapolated.
- Export 600-dpi PNG and editable-text PDF.

## Review Focus

- Missing or duplicate CMIP6 marker rows must raise a useful error rather than silently select data.
- CMIP6 temperature unit must be exactly °C before the shared temperature label is used.
- CMIP7 scenario/config dimensions and required variables must be validated.
- CMIP6 2101–2150 must contain no plotted line or filled data.
- The two rows must use identical x-limits and matching y-limits by column.

---

### Task 1: Build and verify the matched-axis comparison

**Files:**
- Modify: `/Users/tongli1997/Library/CloudStorage/OneDrive-UniversityofVictoria/Onedrive_Desktop/project/Canadian_warming_budget/Sep_Oct_2026/Scenarios/cmip7_ghg_tas_replot.ipynb`
- Create: `/Users/tongli1997/Library/CloudStorage/OneDrive-UniversityofVictoria/Onedrive_Desktop/project/Canadian_warming_budget/Sep_Oct_2026/Scenarios/cmip6_cmip7_ghg_tas_comparison.png`
- Create: `/Users/tongli1997/Library/CloudStorage/OneDrive-UniversityofVictoria/Onedrive_Desktop/project/Canadian_warming_budget/Sep_Oct_2026/Scenarios/cmip6_cmip7_ghg_tas_comparison.pdf`
- Test: `/tmp/test_cmip6_cmip7_comparison.py`

**Interfaces:**
- Consumes: `SSP_IAM_V2_201811.csv` and `cmip7-scenariomip-main/data/fair-outputs/fair_run.nc`.
- Produces: an executed notebook and matched-axis PNG/PDF comparison exports.

- [ ] **Step 1: Write the failing structural and output test**

Assert that the notebook contains both input paths, exact axis limits, CMIP6 marker validation, the two uncertainty definitions, no extrapolation routine, and both output filenames; after execution, assert that all code cells ran without error and both exports are non-empty.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python /tmp/test_cmip6_cmip7_comparison.py`

Expected: FAIL because the current notebook has separate plotting code and no combined exports.

- [ ] **Step 3: Rebuild the notebook as a single comparison workflow**

Keep explicit loading/validation/calculation cells; use `plt.subplots(2, 2, sharex=True)`; set matched column y-limits; shade CMIP6 post-2100 as unavailable without plotting values; preserve the documented CMIP6 and CMIP7 uncertainty distinctions; add separate row legends and a concise methodological caption.

- [ ] **Step 4: Execute the notebook and run the test**

Run `jupyter nbconvert --to notebook --execute cmip7_ghg_tas_replot.ipynb --output cmip7_ghg_tas_replot.ipynb --ExecutePreprocessor.timeout=240`, then `python /tmp/test_cmip6_cmip7_comparison.py`.

Expected: notebook execution exits 0; tests pass; all code cells have execution counts; no error outputs; PNG and PDF exceed 10 KB.

- [ ] **Step 5: Perform visual QA**

Inspect the PNG at original resolution for clipped labels, legend overlap, distinguishable pathways, visible but unobtrusive unavailable-period marking, matched axes, and readable text. Revise and re-run Step 4 if any check fails.
