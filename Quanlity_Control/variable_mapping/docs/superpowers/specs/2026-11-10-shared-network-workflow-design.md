# Shared Network Workflow Design

## Intent

Use one reusable variable-mapping workflow for every network while keeping each network's data and review artifacts visibly isolated.

## Approved layout

```text
variable_mapping/
├── 0.candidate_discovery.ipynb
├── 1.variable_decide.ipynb
├── 2.all_variables_decide.ipynb
├── func/
├── tests/
└── networks/
    └── network_<id>/
        ├── candidate_mappings.csv
        ├── final_variable_rules.csv
        ├── figures/
        └── latest_review/
```

The notebooks expose `NETWORK_ID` as the network switch and derive all other paths from it. `candidate_mappings.csv` and `final_variable_rules.csv` use stable names because the containing directory identifies the network. Single-variable figures stay under that network's `figures/` directory. Batch-review outputs use the stable `latest_review/` directory.

## Latest-review behavior

The batch runner builds a complete review in a staging directory inside the selected network directory. Only after every review artifact is written successfully does it replace `latest_review/`. A failed run leaves the prior `latest_review/` intact. Temporary or backup directories are cleaned after a successful replacement.

## Migration

Rename the three Network 2-specific notebooks to generic names, without retaining duplicate notebook copies. Move the current Network 2 candidate mappings, final rules, and latest batch review into `networks/network_2/`. Clear saved notebook execution output so paths from the old layout are not embedded in the reusable notebooks.

## Constraints and non-goals

- Preserve the contents of current Network 2 CSVs and review artifacts during migration.
- Do not duplicate shared code or notebooks per network.
- Do not alter candidate-selection, QC, plotting, or rule-selection semantics.
- Do not create empty directories for networks that have not been run yet.
- A user starts another network by changing `NETWORK_ID` and running the notebooks in order.

## Approaches considered

- **Shared notebooks with per-network directories — selected:** one maintained workflow and clear data isolation.
- Flat network-prefixed filenames: fewer directories, but becomes cluttered and easier to mix up.
- Full workflow copies per network: visually separated, but duplicated notebooks drift over time.
