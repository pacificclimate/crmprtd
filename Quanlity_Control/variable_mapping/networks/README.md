# Network data folders

Use the shared notebooks in the repository root for every network. Do not copy the
notebooks into these folders.

## Run a network

1. Set `NETWORK_ID` in `0.candidate_discovery.ipynb` and run it to create
   `networks/network_<id>/candidate_mappings.csv`.
2. Use `1.variable_decide.ipynb` for an optional single-variable review, or set the
   same `NETWORK_ID` in `2.all_variables_decide.ipynb` to review all variables.
3. The final selections are saved to `final_variable_rules.csv` in that network's
   folder.

## Folder contents

```text
network_<id>/
├── candidate_mappings.csv       # Candidate variables discovered for this network
├── final_variable_rules.csv     # Saved canonical-variable selections
├── figures/                     # Single-variable plots, created when needed
└── latest_review/               # Latest successful all-variable batch review
```

Each successful batch run replaces only that network's `latest_review/`. A failed
run leaves the previous successful review intact, and other network folders are not
changed.
