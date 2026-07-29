"""Candidate discovery and validation helpers for network variable mappings."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable

import numpy as np
import pandas as pd
import sqlalchemy as sa


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

CANONICAL_VARIABLES = (
    "air_temperature",
    "daily_min_temperature",
    "daily_max_temperature",
    "precipitation_amount",
    "snowfall_amount",
    "snow_depth",
)


@dataclass(frozen=True)
class CanonicalRule:
    unit: str
    plausible_min: float | None
    plausible_max: float | None


CANONICAL_RULES = {
    "air_temperature": CanonicalRule("celsius", -89.4, 57.7),
    "daily_min_temperature": CanonicalRule("celsius", -89.4, 57.7),
    "daily_max_temperature": CanonicalRule("celsius", -89.4, 57.7),
    "precipitation_amount": CanonicalRule("mm", 0.0, 400.0),
    "snowfall_amount": CanonicalRule("cm", 0.0, 1925.0),
    "snow_depth": CanonicalRule("cm", 0.0, 11460.0),
}

CANONICAL_TO_QC_VARIABLE = {
    "air_temperature": "temp",
    "daily_min_temperature": "tmin",
    "daily_max_temperature": "tmax",
    "precipitation_amount": "precip",
    "snowfall_amount": "snw_fall",
    "snow_depth": "snw_dpth",
}


def build_qc_frequency_map(rules: pd.DataFrame) -> dict[str, str]:
    """Map final-rule cadence values to the QC variable names.

    ``exact_timestamp`` is retained as a backward-compatible synonym for
    hourly input. Mixed source cadences are normalized source-by-source by
    :func:`combine_final_rule_observations` and therefore enter QC as daily.
    """
    required = {"canonical_variable", "time_match"}
    missing = required - set(rules.columns)
    if missing:
        raise ValueError(
            f"Final rules are missing frequency columns: {sorted(missing)}"
        )

    frequency_map: dict[str, str] = {}
    for row in rules.itertuples(index=False):
        canonical_variable = row.canonical_variable
        if canonical_variable not in CANONICAL_TO_QC_VARIABLE:
            raise ValueError(
                f"Unknown canonical variable: {canonical_variable}"
            )

        saved_frequency = str(row.time_match).strip().lower()
        if saved_frequency.startswith("mixed:"):
            frequency = "daily"
        else:
            frequency = (
                "hourly" if saved_frequency == "exact_timestamp"
                else saved_frequency
            )
        if frequency not in {"hourly", "daily"}:
            raise ValueError(
                f"Unsupported time_match {row.time_match!r} for "
                f"{canonical_variable}; expected 'hourly' or 'daily'."
            )
        frequency_map[CANONICAL_TO_QC_VARIABLE[canonical_variable]] = frequency

    return frequency_map


def load_candidate_mappings(path: str | Path) -> pd.DataFrame:
    """Load a candidate-mapping registry."""
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
    path: str | Path,
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


def mappings_by_network(path: str | Path) -> dict[int, pd.DataFrame]:
    """Return independently indexed mappings for every network."""
    mappings = load_candidate_mappings(path)
    return {
        int(network_id): rows.drop(columns="network_id").reset_index(drop=True)
        for network_id, rows in mappings.groupby("network_id", sort=True)
    }


def get_candidate_mappings(network_id: int, path: str | Path) -> pd.DataFrame:
    """Load one network's candidate mappings."""
    registries = mappings_by_network(path)
    if int(network_id) not in registries:
        raise KeyError(f"No saved candidate mappings for network {network_id}.")
    return registries[int(network_id)]


def load_final_variable_rules(
    path: str | Path,
    network_id: int,
) -> pd.DataFrame:
    """Load and validate final source-selection rules for one network."""
    rules = pd.read_csv(path)
    required = {
        "network_id", "canonical_variable", "source_vars_ids", "time_match",
        "overlap_method", "single_source_method",
    }
    missing = required - set(rules.columns)
    if missing:
        raise ValueError(f"Final-rule registry is missing columns: {sorted(missing)}")
    rules = rules.loc[rules["network_id"] == int(network_id)].copy()
    rules["source_vars_ids"] = rules["source_vars_ids"].map(json.loads)
    if rules.empty:
        raise ValueError(f"No final variable rules found for network {network_id}.")
    if rules["canonical_variable"].duplicated().any():
        raise ValueError("Final rules must have one row per canonical variable.")
    unknown = set(rules["canonical_variable"]) - set(CANONICAL_TO_QC_VARIABLE)
    if unknown:
        raise ValueError(f"Unknown canonical variables in final rules: {sorted(unknown)}")
    if rules["source_vars_ids"].map(len).eq(0).any():
        raise ValueError("Every final rule must contain at least one source vars_id.")
    return rules.sort_values("canonical_variable").reset_index(drop=True)


def select_stations_with_final_rules(
    engine: sa.Engine,
    rules: pd.DataFrame,
    network_id: int,
) -> pd.DataFrame:
    """Select stations with at least one configured source for every rule."""
    rule_selects = []
    params: dict[str, object] = {"network_id": int(network_id)}
    for index, rule in rules.reset_index(drop=True).iterrows():
        rule_selects.append(
            f"SELECT :canonical_{index} AS canonical_variable, "
            f"CAST(:source_ids_{index} AS integer[]) AS source_vars_ids"
        )
        params[f"canonical_{index}"] = rule["canonical_variable"]
        params[f"source_ids_{index}"] = [int(value) for value in rule["source_vars_ids"]]
    required_rules = " UNION ALL ".join(rule_selects)
    query = sa.text(
        f"""
        WITH required_rules AS ({required_rules})
        SELECT s.station_id, MAX(h.station_name) AS station_name
        FROM meta_station s
        JOIN meta_history h USING (station_id)
        WHERE s.network_id = :network_id
          AND NOT EXISTS (
              SELECT 1
              FROM required_rules r
              WHERE NOT EXISTS (
                  SELECT 1
                  FROM meta_history source_history
                  JOIN obs_raw o USING (history_id)
                  WHERE source_history.station_id = s.station_id
                    AND o.vars_id = ANY(r.source_vars_ids)
                  LIMIT 1
              )
          )
        GROUP BY s.station_id
        ORDER BY s.station_id
        """
    )
    return pd.read_sql(query, engine, params=params)


def fetch_final_rule_observations(
    engine: sa.Engine,
    rules: pd.DataFrame,
    station_ids: Iterable[int],
) -> pd.DataFrame:
    """Fetch all raw observations that participate in the final rules."""
    station_ids = tuple(int(value) for value in station_ids)
    source_ids = tuple(sorted({
        int(source_id)
        for source_ids in rules["source_vars_ids"]
        for source_id in source_ids
    }))
    query = sa.text(
        """
        SELECT h.station_id, h.station_name, o.vars_id, o.obs_time, o.datum
        FROM meta_history h
        JOIN obs_raw o USING (history_id)
        WHERE h.station_id IN :station_ids
          AND o.vars_id IN :source_ids
        ORDER BY h.station_id, o.obs_time, o.vars_id
        """
    ).bindparams(
        sa.bindparam("station_ids", expanding=True),
        sa.bindparam("source_ids", expanding=True),
    )
    return pd.read_sql(
        query, engine, params={"station_ids": station_ids, "source_ids": source_ids}
    )


def combine_final_rule_observations(
    observations: pd.DataFrame,
    rules: pd.DataFrame,
) -> pd.DataFrame:
    """Combine selected sources and normalize mixed cadences to daily.

    Each source is reduced to one value before cross-source averaging, so a
    duplicated source observation cannot receive extra weight. One available
    source is retained automatically when the other source is absent. For a
    ``mixed:ID=frequency,...`` rule, subdaily sources are aggregated to daily
    before they are combined with sources that already report daily values.
    """
    required = {"station_id", "station_name", "vars_id", "obs_time", "datum"}
    missing = required - set(observations.columns)
    if missing:
        raise ValueError(f"Observations are missing columns: {sorted(missing)}")

    source_to_canonical: dict[int, str] = {}
    for _, rule in rules.iterrows():
        for source_id in rule["source_vars_ids"]:
            source_id = int(source_id)
            previous = source_to_canonical.setdefault(
                source_id, rule["canonical_variable"]
            )
            if previous != rule["canonical_variable"]:
                raise ValueError(f"vars_id {source_id} belongs to multiple final rules.")

    combined_input = observations.copy()
    combined_input["canonical_variable"] = combined_input["vars_id"].map(
        source_to_canonical
    )
    combined_input["datum"] = pd.to_numeric(combined_input["datum"], errors="coerce")
    combined_input = combined_input.dropna(
        subset=["canonical_variable", "datum"]
    )
    combined_input["obs_time"] = pd.to_datetime(combined_input["obs_time"])
    exact_parts = []
    daily_parts = []
    daily_aggregations = {
        "air_temperature": "mean",
        "daily_min_temperature": "min",
        "daily_max_temperature": "max",
        "precipitation_amount": "sum",
        "snowfall_amount": "sum",
    }

    for rule in rules.itertuples(index=False):
        canonical_variable = rule.canonical_variable
        source_ids = [int(value) for value in rule.source_vars_ids]
        saved_frequency = str(rule.time_match).strip().lower()
        rule_input = combined_input[
            combined_input["vars_id"].isin(source_ids)
        ].copy()

        if not saved_frequency.startswith("mixed:"):
            exact_parts.append(rule_input)
            continue

        frequency_by_source = {}
        for item in saved_frequency.removeprefix("mixed:").split(","):
            source_text, separator, frequency = item.partition("=")
            if not separator:
                raise ValueError(f"Invalid mixed time_match item: {item!r}")
            frequency_by_source[int(source_text)] = frequency
        missing_frequencies = set(source_ids) - set(frequency_by_source)
        if missing_frequencies:
            raise ValueError(
                "Mixed time_match is missing source frequencies for "
                f"{sorted(missing_frequencies)}"
            )

        for source_id in source_ids:
            source = rule_input[rule_input["vars_id"] == source_id].copy()
            if source.empty:
                continue
            frequency = frequency_by_source[source_id]
            if frequency == "exact_timestamp":
                frequency = "hourly"
            if (
                frequency not in {"hourly", "daily"}
                and not re.fullmatch(r"irregular_([0-9.]+)_hours", frequency)
            ):
                raise ValueError(
                    f"Unsupported source frequency {frequency!r} for "
                    f"vars_id {source_id}"
                )
            source = source.sort_values("obs_time")
            source["obs_time"] = source["obs_time"].dt.floor("D")
            group_columns = [
                "station_id", "station_name", "obs_time", "vars_id",
                "canonical_variable",
            ]

            if frequency == "daily":
                source_daily = (
                    source.groupby(group_columns, as_index=False)
                    .agg(datum=("datum", "first"))
                )
            elif canonical_variable == "snow_depth":
                # Snow depth is an instantaneous state, not an amount to sum.
                # Match the existing QC convention by retaining 04:00 only.
                original_source = rule_input[
                    rule_input["vars_id"] == source_id
                ].copy()
                original_source = original_source[
                    original_source["obs_time"].dt.hour == 4
                ]
                original_source["obs_time"] = (
                    original_source["obs_time"].dt.floor("D")
                )
                source_daily = (
                    original_source.sort_values("obs_time")
                    .groupby(group_columns, as_index=False)
                    .agg(datum=("datum", "first"))
                )
            else:
                aggregation = daily_aggregations[canonical_variable]
                grouped = source.groupby(group_columns)["datum"]
                source_daily = grouped.agg(
                    datum=aggregation, valid_count="count"
                ).reset_index()
                interval_hours = 1.0
                irregular_match = re.fullmatch(
                    r"irregular_([0-9.]+)_hours", frequency
                )
                if irregular_match:
                    interval_hours = float(irregular_match.group(1))
                minimum_count = int(np.ceil(0.75 * 24 / interval_hours))
                source_daily.loc[
                    source_daily["valid_count"] < minimum_count, "datum"
                ] = np.nan
                source_daily = source_daily.drop(columns="valid_count")

            daily_parts.append(source_daily)

    per_source_parts = []
    if exact_parts:
        exact_input = pd.concat(exact_parts, ignore_index=True)
        per_source_parts.append(
            exact_input.groupby(
                ["station_id", "station_name", "obs_time", "vars_id",
                 "canonical_variable"],
                as_index=False,
            ).agg(datum=("datum", "mean"))
        )
    if daily_parts:
        per_source_parts.append(pd.concat(daily_parts, ignore_index=True))
    if not per_source_parts:
        return pd.DataFrame(columns=[
            "station_id", "station_name", "obs_time", "net_var_name", "datum",
        ])
    per_source = pd.concat(per_source_parts, ignore_index=True)
    combined = (
        per_source
        .groupby(
            ["station_id", "station_name", "obs_time", "canonical_variable"],
            as_index=False,
        )
        .agg(datum=("datum", "mean"))
    )
    combined["net_var_name"] = combined["canonical_variable"].map(
        CANONICAL_TO_QC_VARIABLE
    )
    return combined[[
        "station_id", "station_name", "obs_time", "net_var_name", "datum",
    ]].sort_values(["station_id", "obs_time", "net_var_name"]).reset_index(drop=True)


def select_candidate_stations(
    engine: sa.Engine,
    vars_ids: Iterable[int],
    network_id: int = 2,
    limit: int = 5,
    offset: int = 0,
) -> pd.DataFrame:
    """Select stations containing every requested candidate variable."""
    vars_ids = tuple(int(value) for value in vars_ids)
    query = sa.text(
        """
        SELECT s.station_id, MAX(h.station_name) AS station_name
        FROM meta_station s
        JOIN meta_history h USING (station_id)
        WHERE s.network_id = :network_id
          AND NOT EXISTS (
              SELECT 1
              FROM unnest(CAST(:vars_ids AS integer[])) AS requested(vars_id)
              WHERE NOT EXISTS (
                  SELECT 1
                  FROM meta_history candidate_history
                  JOIN obs_raw o USING (history_id)
                  WHERE candidate_history.station_id = s.station_id
                    AND o.vars_id = requested.vars_id
                  LIMIT 1
              )
          )
        GROUP BY s.station_id
        ORDER BY s.station_id
        LIMIT :station_limit
        OFFSET :station_offset
        """
    )
    return pd.read_sql(
        query,
        engine,
        params={"network_id": network_id, "vars_ids": list(vars_ids),
                "station_limit": int(limit), "station_offset": int(offset)},
    )


def summarize_variable_station_presence(
    engine: sa.Engine,
    vars_ids: Iterable[int],
    network_id: int = 2,
) -> pd.DataFrame:
    """List stations having at least one non-null observation per variable.

    EXISTS lets PostgreSQL stop searching as soon as it finds a qualifying
    observation, avoiding the full time-series aggregation performed by
    ``profile_candidate_variables``.
    """
    vars_ids = tuple(int(value) for value in vars_ids)
    query = sa.text(
        """
        WITH stations AS (
            SELECT s.station_id, MAX(h.station_name) AS station_name
            FROM meta_station s
            JOIN meta_history h USING (station_id)
            WHERE s.network_id = :network_id
            GROUP BY s.station_id
        )
        SELECT requested.vars_id,
               MAX(v.net_var_name::text) AS net_var_name,
               COUNT(DISTINCT stations.station_id) AS station_count,
               STRING_AGG(
                   DISTINCT stations.station_id::text, ', '
                   ORDER BY stations.station_id::text
               ) AS station_ids,
               STRING_AGG(
                   DISTINCT stations.station_name, '; '
                   ORDER BY stations.station_name
               ) AS station_names
        FROM stations
        CROSS JOIN unnest(CAST(:vars_ids AS integer[]))
            AS requested(vars_id)
        JOIN meta_vars v ON v.vars_id = requested.vars_id
        WHERE EXISTS (
              SELECT 1
              FROM obs_raw o
              JOIN meta_history observation_history USING (history_id)
              WHERE observation_history.station_id = stations.station_id
                AND o.vars_id = requested.vars_id
                AND o.datum IS NOT NULL
              LIMIT 1
          )
        GROUP BY requested.vars_id
        ORDER BY requested.vars_id
        """
    )
    return pd.read_sql(
        query,
        engine,
        params={"network_id": network_id, "vars_ids": list(vars_ids)},
    )


def profile_candidate_variables(
    engine: sa.Engine,
    vars_ids: Iterable[int],
    network_id: int = 2,
    station_ids: Iterable[int] | None = None,
) -> pd.DataFrame:
    """Profile candidate-variable coverage by station in years."""
    vars_ids = tuple(int(value) for value in vars_ids)
    station_ids = tuple(int(value) for value in (station_ids or ()))
    station_filter = " AND s.station_id IN :station_ids" if station_ids else ""
    query = sa.text(
        """
        SELECT h.station_id, MAX(h.station_name) AS station_name, o.vars_id,
               v.net_var_name::text AS net_var_name,
               COUNT(DISTINCT EXTRACT(YEAR FROM o.obs_time)) AS active_years,
               MIN(o.obs_time) AS first_observation,
               MAX(o.obs_time) AS last_observation,
               MIN(o.datum) AS observed_min,
               MAX(o.datum) AS observed_max
        FROM obs_raw o
        JOIN meta_history h USING (history_id)
        JOIN meta_station s USING (station_id)
        JOIN meta_vars v USING (vars_id)
        WHERE s.network_id = :network_id AND o.vars_id IN :vars_ids
        """ + station_filter + """
        GROUP BY h.station_id, o.vars_id, v.net_var_name
        ORDER BY h.station_id, o.vars_id
        """
    ).bindparams(sa.bindparam("vars_ids", expanding=True))
    if station_ids:
        query = query.bindparams(sa.bindparam("station_ids", expanding=True))
    params = {"network_id": network_id, "vars_ids": vars_ids}
    if station_ids:
        params["station_ids"] = station_ids
    profile = pd.read_sql(query, engine, params=params)
    if profile.empty:
        return profile
    coverage_years = (
        profile["last_observation"] - profile["first_observation"]
    ).dt.total_seconds().div(86400 * 365.25).add(1 / 365.25)
    profile.insert(profile.columns.get_loc("active_years") + 1,
                   "coverage_years", coverage_years)
    return profile


def summarize_candidate_profiles(profile: pd.DataFrame) -> pd.DataFrame:
    """Create a variable-level reach and coverage summary."""
    if profile.empty:
        return pd.DataFrame()
    return (
        profile.groupby(["vars_id", "net_var_name"], as_index=False)
        .agg(
            station_count=("station_id", "nunique"),
            first_observation=("first_observation", "min"),
            last_observation=("last_observation", "max"),
            median_station_span_years=("coverage_years", "median"),
            median_active_years=("active_years", "median"),
        )
        .sort_values(["station_count", "median_active_years"], ascending=False)
    )


def fetch_candidate_observations(
    engine: sa.Engine,
    vars_ids: Iterable[int],
    station_ids: Iterable[int],
) -> pd.DataFrame:
    """Load candidate time-series values for selected stations."""
    vars_ids = tuple(int(value) for value in vars_ids)
    station_ids = tuple(int(value) for value in station_ids)
    query = sa.text(
        """
        SELECT h.station_id, h.station_name, o.vars_id,
               v.net_var_name::text AS net_var_name,
               o.obs_time, o.datum
        FROM obs_raw o
        JOIN meta_history h USING (history_id)
        JOIN meta_vars v USING (vars_id)
        WHERE o.vars_id IN :vars_ids
          AND h.station_id IN :station_ids
        ORDER BY h.station_id, o.obs_time, o.vars_id
        """
    ).bindparams(sa.bindparam("vars_ids", expanding=True),
                 sa.bindparam("station_ids", expanding=True))
    return pd.read_sql(query, engine,
                       params={"vars_ids": vars_ids, "station_ids": station_ids})


def apply_canonical_rule(
    observations: pd.DataFrame,
    canonical_variable: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Remove null, non-finite, and out-of-range values."""
    rule = CANONICAL_RULES[canonical_variable]
    datum = pd.to_numeric(observations["datum"], errors="coerce")
    keep = np.isfinite(datum)
    if rule.plausible_min is not None:
        keep &= datum >= rule.plausible_min
    if rule.plausible_max is not None:
        keep &= datum <= rule.plausible_max
    cleaned = observations.loc[keep].copy()
    cleaned["datum"] = datum.loc[keep]
    summary = (
        observations.assign(removed=~keep)
        .groupby(["station_id", "net_var_name"], as_index=False)
        .agg(row_count=("datum", "size"), removed_count=("removed", "sum"))
    )
    summary["removed_pct"] = 100 * summary["removed_count"] / summary["row_count"]
    return cleaned, summary
