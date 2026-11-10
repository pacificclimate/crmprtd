# CMIP6–CMIP7 pathway comparison figure

## Intent

Create a directly comparable four-panel figure showing how the selected CMIP6 ScenarioMIP marker pathways differ from the indicative CMIP7 ScenarioMIP pathways in greenhouse-gas emissions and global-mean warming.

## Figure contract

- Core conclusion: matched axes reveal differences in pathway range, timing, and warming outcomes between the CMIP6 and CMIP7 scenario sets.
- Evidence chain: CMIP6 emissions and MAGICC6 temperature form the top row; CMIP7 emissions and FaIR temperature form the bottom row.
- Archetype: quantitative 2 x 2 grid.
- Backend: Python/matplotlib only.
- Exports: an executed self-contained notebook plus 600-dpi PNG and editable-text PDF.

## Design

- Columns: GHG emissions on the left; global-mean temperature change on the right.
- Rows: CMIP6 on top; CMIP7 on the bottom.
- Every panel uses the same 2000–2150 x-axis.
- Both emissions panels use the same y-limits (-50 to 100 Gt CO2-eq yr-1).
- Both temperature panels use the same y-limits (0 to 5 degrees C/K above 1850–1900).
- CMIP6 curves stop at 2100. The 2101–2150 area remains blank and is labeled as unavailable; no extrapolation is made.
- CMIP6 emissions use the illustrative half-width approaching +/-8 Gt CO2-eq yr-1.
- CMIP6 temperature is shown as marker pathways without uncertainty shading because the provided IAM CSV contains one MAGICC6 diagnostic per marker.
- CMIP7 emissions retain the authors' illustrative range and hatched extension period.
- CMIP7 temperature retains the FaIR 33rd–66th percentile bands.
- Separate compact legends identify CMIP6 SSP pathways and CMIP7 indicative pathway classes.

## Approaches considered

1. Selected: 2 x 2 grid with matched axes. It keeps uncertainty definitions honest and supports direct row-wise comparison.
2. Overlay CMIP6 and CMIP7 in two panels. Rejected because thirteen pathways plus uncertainty bands would obscure individual trajectories.
3. Separate figures. Rejected because visual comparison would depend on page placement and invite unnoticed scale differences.

## Integrity and review risks

- Do not imply that CMIP6 MAGICC6 lines and CMIP7 FaIR percentiles have equivalent uncertainty information.
- Preserve the different temporal coverage explicitly.
- Validate temperature units and baseline metadata from the CSV before labeling both temperature axes as 1850–1900 anomalies.
- Do not connect or extrapolate CMIP6 data beyond 2100.
