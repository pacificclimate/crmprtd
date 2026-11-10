# CMIP7 Self-Contained Figure 4 Notebook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `cmip7_ghg_tas_replot.ipynb` with a self-contained plotting notebook that loads the authors' cached FaIR NetCDF, reproduces the Figure 4 calculations, and exports the two-panel figure without importing repository scripts.

**Architecture:** One notebook will define paths, validate and load `fair_run.nc`, expose and document the original gas-by-gas/GWP provenance of `co2e`, calculate the emissions band and temperature anomalies/quantiles, and render/export the figure. It will preserve the authors' numerical choices while making every intermediate inspectable in notebook cells.

**Tech Stack:** Python, Jupyter, NumPy, pandas, xarray, matplotlib, NetCDF4.

**Spec:** Conversation-approved lightweight self-contained design: use the existing FaIR NetCDF rather than rerunning FaIR; remove all current target cells; include import, validation, calculations, plotting, and PNG/PDF export.

## Global Constraints

- Use Python exclusively for calculations, drawing, previewing, and exports.
- Do not import `scripts.plotting` or any other authors' helper module.
- Use `cmip7-scenariomip-main/data/fair-outputs/fair_run.nc` as the primary input.
- Explain that `co2e` originated from `fair-inputs/emissions_1750-2500.csv` and AR6 GWP100 factors in `fair-inputs/gwp_mass_adjusted_100y.csv`.
- Match the authors' Figure 4 calculations: 1850–1901 time-bound mean baseline, 0.33–0.66 temperature quantiles, and time-dependent emissions half-width approaching 8 Gt CO2-eq yr-1.
- Export `cmip7_ghg_tas_replot.png` at 600 dpi and `cmip7_ghg_tas_replot.pdf` beside the notebook.

## Review Focus

- Missing NetCDF: raise a clear `FileNotFoundError` naming the expected relative location.
- Wrong dataset schema: validate required coordinates and variables before calculation.
- Scenario order: use the NetCDF coordinate order and verify the uncertainty-width endpoints correspond to VL and H as in the authors' code.
- Time-coordinate mismatch: keep `timepoints` for emissions and `timebounds` for temperature, with aligned array lengths in each `fill_between` call.
- Notebook portability: resolve paths from the notebook folder and avoid dependence on the process's initial working directory where practical.

---

### Task 1: Rebuild and verify the notebook

**Files:**
- Modify: `/Users/tongli1997/Library/CloudStorage/OneDrive-UniversityofVictoria/Onedrive_Desktop/project/Canadian_warming_budget/Sep_Oct_2026/Scenarios/cmip7_ghg_tas_replot.ipynb`
- Test: `/tmp/test_cmip7_ghg_tas_replot.py`

**Interfaces:**
- Consumes: `cmip7-scenariomip-main/data/fair-outputs/fair_run.nc` with `emissions`, `co2e`, `temperature`, `timepoints`, `timebounds`, `scenario`, and `config`.
- Produces: an executed notebook plus `cmip7_ghg_tas_replot.png` and `cmip7_ghg_tas_replot.pdf`.

- [ ] **Step 1: Write the failing notebook-structure test**

Assert that the target notebook contains no `import plotting`, references the required NetCDF and source CSV filenames, validates required variables, calculates `emissions_half_width`, calculates the 1850–1901 baseline and 0.33/0.66 quantiles, calls `fill_between`, and exports PNG/PDF.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python /tmp/test_cmip7_ghg_tas_replot.py`

Expected: FAIL because the current notebook lacks the complete self-contained data provenance, emissions panel, and export pipeline.

- [ ] **Step 3: Replace the notebook cells**

Create ordered markdown/code cells for: purpose and provenance; imports and relative paths; dataset validation/summary; emissions and temperature calculations; Figure 4 rendering; PNG/PDF export; compact 2100 diagnostic table; dataset close.

- [ ] **Step 4: Execute the notebook**

Run `jupyter nbconvert --to notebook --execute cmip7_ghg_tas_replot.ipynb --output cmip7_ghg_tas_replot.ipynb --ExecutePreprocessor.timeout=180` from the `Scenarios` folder.

Expected: exit code 0; all code cells receive execution counts; no error outputs.

- [ ] **Step 5: Run automated verification**

Run the notebook-structure test and verify both exports exist and exceed 10 KB.

Expected: all assertions pass.

- [ ] **Step 6: Perform Python-only visual QA**

Open the generated PNG and verify: two readable panels; no clipped axes, legend, or labels; emissions bands and temperature bands visible; hatching after 2100; scenario colors consistent; caption/provenance readable.

- [ ] **Step 7: Report the outputs and exact GHG provenance**

Link the executed notebook and both exports, and state that panel-(a) reads `co2e` from the cached NetCDF, originally derived from gas-by-gas emissions and AR6 GWP100 factors.
