#!/usr/bin/env python3
"""Apply the simplified daily aggregation schema to saved candidate CSVs."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tempfile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "func"))
from func_variable_mapping import (  # noqa: E402
    MAPPING_COLUMNS,
    add_candidate_daily_processing,
    load_candidate_mappings,
)


REMOVED_COLUMNS = [
    "daily_boundary_hour", "daily_time_basis", "daily_processing_status",
]
COMBINED_COLUMNS = [
    "network_id", "canonical_variable", "vars_id", "net_var_name",
    "standard_name", "cell_method", "long_description", "display_name",
    "network_station_count", "source_time_scale", "daily_aggregation",
]
KEY = ["network_id", "vars_id", "canonical_variable"]


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", prefix=f".{path.stem}_",
            dir=path.parent, delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            frame.to_csv(temporary, index=False)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _final_source_snapshot(networks_dir: Path) -> list[tuple]:
    rows = []
    for path in sorted(networks_dir.rglob("*final_variable_rules.csv")):
        frame = pd.read_csv(path)
        for row in frame.to_dict("records"):
            rows.append((
                str(path.relative_to(networks_dir)),
                int(float(row["network_id"])),
                row["canonical_variable"],
                row.get("source_vars_ids"),
            ))
    return rows


def migrate(networks_dir: Path = ROOT / "networks") -> dict[str, int]:
    """Update existing outputs without database queries or final-rule changes."""
    networks_dir = Path(networks_dir)
    combined_path = networks_dir / "all_networks_candidate_mappings.csv"
    combined_before = pd.read_csv(combined_path)
    metadata_columns = [
        "vars_id", "net_var_name", "standard_name", "cell_method",
        "long_description", "display_name",
    ]
    metadata = combined_before[metadata_columns].drop_duplicates("vars_id")
    final_sources_before = _final_source_snapshot(networks_dir)

    pending: dict[Path, pd.DataFrame] = {}
    classified_frames = []
    candidate_paths = sorted(
        networks_dir.glob("network_*/net*_candidate_mappings.csv"))
    for path in candidate_paths:
        match = re.fullmatch(
            r"network_(\d+)/net(\d+)_candidate_mappings\.csv",
            path.relative_to(networks_dir).as_posix(),
        )
        if match is None or match.group(1) != match.group(2):
            raise ValueError(f"Invalid network candidate path: {path}")
        loaded = load_candidate_mappings(path)
        classified = add_candidate_daily_processing(loaded, metadata)
        classified = classified.sort_values(
            ["network_id", "canonical_variable", "priority", "vars_id"],
            kind="stable",
        ).reset_index(drop=True)
        pending[path] = classified[MAPPING_COLUMNS]
        classified_frames.append(classified[MAPPING_COLUMNS])

    all_candidates = pd.concat(classified_frames, ignore_index=True)
    if all_candidates.duplicated(KEY).any():
        raise ValueError("Duplicate candidate keys found during migration.")
    if len(all_candidates) != len(combined_before):
        raise ValueError(
            f"Candidate row mismatch: {len(all_candidates)} registries versus "
            f"{len(combined_before)} combined rows.")

    aggregations = all_candidates[KEY + ["daily_aggregation"]]
    review_paths = sorted(
        networks_dir.glob("network_*/latest_review/net*_candidate_review.csv"))
    updated_reviews = 0
    for path in review_paths:
        review = pd.read_csv(path)
        if "daily_aggregation" not in review.columns:
            continue
        updated = review.drop(
            columns=["daily_aggregation", *REMOVED_COLUMNS], errors="ignore",
        ).merge(aggregations, on=KEY, how="left", validate="one_to_one")
        if updated["daily_aggregation"].isna().any():
            raise ValueError(f"Missing daily aggregation while updating {path}.")
        updated["decision"] = updated["decision"].replace(
            "daily processing review", "manual decision")
        columns = [name for name in updated.columns if name != "daily_aggregation"]
        position = columns.index("canonical_variable") + 1
        columns.insert(position, "daily_aggregation")
        pending[path] = updated[columns]
        updated_reviews += 1

    combined = combined_before.drop(
        columns=["daily_aggregation", *REMOVED_COLUMNS], errors="ignore",
    ).merge(aggregations, on=KEY, how="left", validate="one_to_one")
    if combined["daily_aggregation"].isna().any():
        raise ValueError("Combined output is missing daily aggregations.")
    combined = combined[COMBINED_COLUMNS].sort_values(
        ["network_id", "canonical_variable", "vars_id", "net_var_name"],
        kind="stable",
    ).reset_index(drop=True)
    pending[combined_path] = combined

    if _final_source_snapshot(networks_dir) != final_sources_before:
        raise AssertionError("Final source selections changed before CSV writes.")
    for path, frame in pending.items():
        _atomic_csv(frame, path)
    if _final_source_snapshot(networks_dir) != final_sources_before:
        raise AssertionError("Final source selections changed during migration.")

    summary = {
        "candidate_files": len(candidate_paths),
        "review_files": updated_reviews,
        "combined_files": 1,
        "candidate_rows": len(all_candidates),
    }
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    migrate()
