
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
import sqlalchemy as sa

from candidate_mappings import (
    CANDIDATE_MAPPINGS_BY_NETWORK,
    get_candidate_mappings,
    load_candidate_mappings,
    save_candidate_mappings,
)


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


def select_candidate_stations(
    engine: sa.Engine,
    vars_ids: Iterable[int],
    network_id: int = 2,
    limit: int = 5,
    offset: int = 0,
) -> pd.DataFrame:
    """Select a page of stations that has every requested variable."""
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


def profile_candidate_variables(
    engine: sa.Engine,
    vars_ids: Iterable[int],
    network_id: int = 2,
    station_ids: Iterable[int] | None = None,
) -> pd.DataFrame:
    """Profile variables by station using observations, not metadata alone."""
    vars_ids = tuple(int(value) for value in vars_ids)
    station_ids = tuple(int(value) for value in (station_ids or ()))
    station_filter = " AND s.station_id IN :station_ids" if station_ids else ""
    query = sa.text(
        """
        SELECT h.station_id, MAX(h.station_name) AS station_name, o.vars_id,
               v.net_var_name::text AS net_var_name,
               COUNT(*) AS row_count,
               COUNT(o.datum) AS nonnull_count,
               COUNT(DISTINCT o.obs_time::date) AS active_days,
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
    profile = pd.read_sql(
        query, engine, params=params
    )
    if profile.empty:
        return profile
    profile["coverage_days"] = (
        profile["last_observation"] - profile["first_observation"]
    ).dt.total_seconds().div(86400).add(1)
    profile["active_day_pct"] = 100 * profile["active_days"] / profile["coverage_days"]
    profile["nonnull_pct"] = 100 * profile["nonnull_count"] / profile["row_count"]
    return profile


def summarize_candidate_profiles(profile: pd.DataFrame) -> pd.DataFrame:
    """Create a variable-level reach and coverage summary."""
    if profile.empty:
        return pd.DataFrame()
    return (
        profile.groupby(["vars_id", "net_var_name"], as_index=False)
        .agg(
            station_count=("station_id", "nunique"),
            total_rows=("row_count", "sum"),
            total_nonnull=("nonnull_count", "sum"),
            first_observation=("first_observation", "min"),
            last_observation=("last_observation", "max"),
            median_station_span_days=("coverage_days", "median"),
            median_active_days=("active_days", "median"),
            median_active_day_pct=("active_day_pct", "median"),
            median_nonnull_pct=("nonnull_pct", "median"),
        )
        .sort_values(["station_count", "total_nonnull"], ascending=False)
    )


def fetch_candidate_observations(
    engine: sa.Engine,
    vars_ids: Iterable[int],
    station_ids: Iterable[int],
) -> pd.DataFrame:
    """Load time-series values for selected variables and stations."""
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
    ).bindparams(
        sa.bindparam("vars_ids", expanding=True),
        sa.bindparam("station_ids", expanding=True),
    )
    return pd.read_sql(
        query, engine,
        params={"vars_ids": vars_ids, "station_ids": station_ids},
    )


def apply_canonical_rule(
    observations: pd.DataFrame,
    canonical_variable: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Remove null, non-finite, and out-of-range values for one canonical variable."""
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
