"""Persistent candidate-variable registries keyed by network_id."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REGISTRY_PATH = Path(__file__).with_name("candidate_mappings.csv")
MAPPING_COLUMNS = [
    "network_id",
    "vars_id",
    "net_var_name",
    "canonical_variable",
    "daily_aggregation",
    "priority",
    "source_family",
    "mapping_status",
]


def load_candidate_mappings(path: str | Path = REGISTRY_PATH) -> pd.DataFrame:
    """Load all saved network mappings from one CSV file."""
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=MAPPING_COLUMNS)
    mappings = pd.read_csv(path)
    missing = set(MAPPING_COLUMNS) - set(mappings.columns)
    if missing:
        raise ValueError(f"Candidate registry is missing columns: {sorted(missing)}")
    return mappings[MAPPING_COLUMNS].sort_values(
        ["network_id", "canonical_variable", "priority", "vars_id"]
    ).reset_index(drop=True)


def save_candidate_mappings(
    network_id: int,
    mappings: pd.DataFrame,
    path: str | Path = REGISTRY_PATH,
) -> pd.DataFrame:
    """Replace one network's rows and save the combined registry."""
    path = Path(path)
    required = set(MAPPING_COLUMNS) - {"network_id"}
    missing = required - set(mappings.columns)
    if missing:
        raise ValueError(f"Mappings are missing columns: {sorted(missing)}")

    new_rows = mappings.copy()
    new_rows["network_id"] = int(network_id)
    existing = load_candidate_mappings(path)
    existing = existing[existing["network_id"] != int(network_id)]
    combined = pd.concat([existing, new_rows[MAPPING_COLUMNS]], ignore_index=True)
    combined = combined.sort_values(
        ["network_id", "canonical_variable", "priority", "vars_id"]
    ).reset_index(drop=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(path, index=False)
    return combined


def mappings_by_network(path: str | Path = REGISTRY_PATH) -> dict[int, pd.DataFrame]:
    """Return independently indexed DataFrames for every saved network."""
    mappings = load_candidate_mappings(path)
    return {
        int(network_id): rows.drop(columns="network_id").reset_index(drop=True)
        for network_id, rows in mappings.groupby("network_id", sort=True)
    }


def get_candidate_mappings(
    network_id: int,
    path: str | Path = REGISTRY_PATH,
) -> pd.DataFrame:
    """Load one network registry or raise a useful error."""
    registries = mappings_by_network(path)
    if int(network_id) not in registries:
        raise KeyError(
            f"No saved candidate mappings for network {network_id}. "
            "Run the candidate-discovery notebook and save its reviewed result."
        )
    return registries[int(network_id)]


CANDIDATE_MAPPINGS_BY_NETWORK = mappings_by_network()
