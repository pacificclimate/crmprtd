"""Variable discovery and mapping helpers for the network-2 QC prototype.

This module deliberately stops at *mapping recommendations*.  A candidate is
not treated as approved merely because its name resembles a canonical QC
variable.  The notebook uses these helpers to compare metadata, coverage,
cadence, plausible ranges, and overlapping source series.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
import sqlalchemy as sa


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


# Candidate registry for network 2. Status remains "candidate" until the
# overlap/semantics review in the notebook is accepted by a domain reviewer.
CANDIDATE_MAPPINGS = pd.DataFrame(
    [
        (721, "air_temp", "air_temperature", "point", "mean", 1, "modern"),
        (434, "CURRENT_AIR_TEMPERATURE1", "air_temperature", "point", "mean", 2, "legacy"),
        (436, "CURRENT_AIR_TEMPERATURE2", "air_temperature", "point", "mean", 3, "legacy_fallback"),
        (722, "min_air_temp_snc_last_reset", "daily_min_temperature", "running_minimum", "last", 1, "modern"),
        (435, "MINIMUM_AIR_TEMPERATURE", "daily_min_temperature", "interval_minimum", "min", 2, "legacy"),
        (720, "max_air_temp_snc_last_reset", "daily_max_temperature", "running_maximum", "last", 1, "modern"),
        (433, "MAXIMUM_AIR_TEMPERATURE", "daily_max_temperature", "interval_maximum", "max", 2, "legacy"),
        (726, "pcpn_amt_pst1hr", "precipitation_amount", "one_hour_amount", "sum", 1, "modern"),
        (442, "HOURLY_PRECIPITATION", "precipitation_amount", "hourly_or_daily_amount", "review", 2, "legacy"),
        (728, "snwfl_amt_pst1hr", "snowfall_amount", "one_hour_amount", "sum", 1, "modern"),
        (451, "STANDARD_SNOW", "snowfall_amount", "interval_amount", "review", 2, "legacy"),
        (727, "snw_dpth", "snow_depth", "point", "fixed_hour", 1, "modern"),
        (450, "HEIGHT_OF_SNOW", "snow_depth", "point", "fixed_hour", 2, "legacy"),
    ],
    columns=[
        "vars_id",
        "net_var_name",
        "canonical_variable",
        "source_type",
        "daily_aggregation",
        "priority",
        "source_family",
    ],
)
CANDIDATE_MAPPINGS["mapping_status"] = "candidate"


def select_smallest_stations(engine: sa.Engine, network_id: int = 2, limit: int = 3) -> pd.DataFrame:
    """Return station/history metadata for the smallest station IDs."""
    query = sa.text(
        """
        WITH chosen AS (
            SELECT station_id, native_id, min_obs_time, max_obs_time
            FROM meta_station
            WHERE network_id = :network_id
            ORDER BY station_id
            LIMIT :limit
        )
        SELECT c.station_id, c.native_id, c.min_obs_time, c.max_obs_time,
               h.history_id, h.station_name, h.lon, h.lat, h.elev,
               h.sdate, h.edate, h.tz_offset, h.freq
        FROM chosen c
        LEFT JOIN meta_history h USING (station_id)
        ORDER BY c.station_id, h.sdate NULLS FIRST, h.history_id
        """
    )
    return pd.read_sql(query, engine, params={"network_id": network_id, "limit": limit})


def fetch_network_catalog(engine: sa.Engine, network_id: int = 2) -> pd.DataFrame:
    """Return all variable metadata registered for a network."""
    query = sa.text(
        """
        SELECT vars_id, network_id, net_var_name::text AS net_var_name, unit,
               precision, standard_name, cell_method, long_description,
               display_name, short_name
        FROM meta_vars
        WHERE network_id = :network_id
        ORDER BY net_var_name
        """
    )
    return pd.read_sql(query, engine, params={"network_id": network_id})


def fetch_available_variables(engine: sa.Engine, histories: pd.DataFrame) -> pd.DataFrame:
    """Efficiently enumerate vars_id values present in selected histories.

    PostgreSQL does not always optimize ``SELECT DISTINCT`` well for the very
    large obs_raw table.  This recursive loose-index scan walks the composite
    (history_id, vars_id, obs_time) index instead of scanning every observation.
    """
    history_ids = tuple(int(x) for x in histories["history_id"].dropna().unique())
    if not history_ids:
        return pd.DataFrame()

    query = sa.text(
        """
        WITH RECURSIVE histories AS (
            SELECT history_id, station_id, station_name
            FROM meta_history
            WHERE history_id IN :history_ids
        ),
        distinct_vars(history_id, station_id, station_name, vars_id) AS (
            SELECT h.history_id, h.station_id, h.station_name,
                   (SELECT MIN(o.vars_id) FROM obs_raw o
                    WHERE o.history_id = h.history_id)
            FROM histories h
            UNION ALL
            SELECT d.history_id, d.station_id, d.station_name,
                   (SELECT MIN(o.vars_id) FROM obs_raw o
                    WHERE o.history_id = d.history_id AND o.vars_id > d.vars_id)
            FROM distinct_vars d
            WHERE d.vars_id IS NOT NULL
        )
        SELECT d.station_id, d.history_id, d.station_name, v.vars_id,
               v.net_var_name::text AS net_var_name, v.unit, v.standard_name,
               v.cell_method, v.display_name, v.short_name, v.long_description
        FROM distinct_vars d
        JOIN meta_vars v USING (vars_id)
        ORDER BY d.station_id, d.history_id, v.net_var_name
        """
    ).bindparams(sa.bindparam("history_ids", expanding=True))
    return pd.read_sql(query, engine, params={"history_ids": history_ids})


def profile_candidates(engine: sa.Engine, histories: pd.DataFrame) -> pd.DataFrame:
    """Calculate coverage and raw ranges for all registered candidates."""
    history_ids = tuple(int(x) for x in histories["history_id"].dropna().unique())
    vars_ids = tuple(int(x) for x in CANDIDATE_MAPPINGS["vars_id"].unique())
    if not history_ids:
        return pd.DataFrame()

    query = sa.text(
        """
        SELECT h.station_id, h.station_name, o.history_id, o.vars_id,
               v.net_var_name::text AS net_var_name, v.unit, v.standard_name,
               v.cell_method, COUNT(*) AS row_count,
               COUNT(o.datum) AS nonnull_count,
               MIN(o.obs_time) AS first_observation,
               MAX(o.obs_time) AS last_observation,
               MIN(o.datum) AS observed_min,
               MAX(o.datum) AS observed_max
        FROM obs_raw o
        JOIN meta_history h USING (history_id)
        JOIN meta_vars v USING (vars_id)
        WHERE o.history_id IN :history_ids AND o.vars_id IN :vars_ids
        GROUP BY h.station_id, h.station_name, o.history_id, o.vars_id,
                 v.net_var_name, v.unit, v.standard_name, v.cell_method
        ORDER BY h.station_id, o.vars_id
        """
    ).bindparams(
        sa.bindparam("history_ids", expanding=True),
        sa.bindparam("vars_ids", expanding=True),
    )
    profile = pd.read_sql(
        query,
        engine,
        params={"history_ids": history_ids, "vars_ids": vars_ids},
    )
    profile = profile.merge(CANDIDATE_MAPPINGS, on=["vars_id", "net_var_name"], how="inner")
    profile["coverage_days"] = (
        profile["last_observation"] - profile["first_observation"]
    ).dt.total_seconds().div(86400).add(1)
    profile["rows_per_coverage_day"] = profile["row_count"] / profile["coverage_days"]
    return profile


def fetch_candidate_observations(
    engine: sa.Engine,
    history_ids: Iterable[int],
    vars_ids: Iterable[int] | None = None,
) -> pd.DataFrame:
    """Load candidate observations for detailed cadence and overlap review."""
    history_ids = tuple(int(x) for x in history_ids)
    if vars_ids is None:
        vars_ids = CANDIDATE_MAPPINGS["vars_id"].unique()
    vars_ids = tuple(int(x) for x in vars_ids)
    query = sa.text(
        """
        SELECT h.station_id, h.station_name, o.history_id, o.vars_id,
               v.net_var_name::text AS net_var_name, o.obs_time, o.datum
        FROM obs_raw o
        JOIN meta_history h USING (history_id)
        JOIN meta_vars v USING (vars_id)
        WHERE o.history_id IN :history_ids AND o.vars_id IN :vars_ids
        ORDER BY h.station_id, o.vars_id, o.obs_time
        """
    ).bindparams(
        sa.bindparam("history_ids", expanding=True),
        sa.bindparam("vars_ids", expanding=True),
    )
    observations = pd.read_sql(
        query,
        engine,
        params={"history_ids": history_ids, "vars_ids": vars_ids},
    )
    observations["obs_time"] = pd.to_datetime(observations["obs_time"])
    return observations


def add_observation_diagnostics(observations: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return observation-level validity fields and a candidate-level summary."""
    data = observations.merge(
        CANDIDATE_MAPPINGS,
        on=["vars_id", "net_var_name"],
        how="inner",
    )
    # One physical source may be a candidate for multiple canonical outputs
    # (air_temp also provides fallback daily extrema), so diagnostics are
    # intentionally canonical-variable specific.
    rule_frame = pd.DataFrame(
        [
            {
                "canonical_variable": name,
                "plausible_min": rule.plausible_min,
                "plausible_max": rule.plausible_max,
                "target_unit": rule.unit,
            }
            for name, rule in CANONICAL_RULES.items()
        ]
    )
    data = data.merge(rule_frame, on="canonical_variable", how="left")
    data["is_nonfinite"] = ~np.isfinite(data["datum"])
    data["below_plausible"] = data["plausible_min"].notna() & (
        data["datum"] < data["plausible_min"]
    )
    data["above_plausible"] = data["plausible_max"].notna() & (
        data["datum"] > data["plausible_max"]
    )
    data["is_implausible"] = data[
        ["is_nonfinite", "below_plausible", "above_plausible"]
    ].any(axis=1)

    keys = ["station_id", "station_name", "vars_id", "net_var_name", "canonical_variable"]
    summary = (
        data.groupby(keys, dropna=False)
        .agg(
            row_count=("datum", "size"),
            valid_numeric_count=("datum", "count"),
            implausible_count=("is_implausible", "sum"),
            raw_min=("datum", "min"),
            raw_median=("datum", "median"),
            raw_max=("datum", "max"),
            first_observation=("obs_time", "min"),
            last_observation=("obs_time", "max"),
        )
        .reset_index()
    )
    summary["implausible_pct"] = 100 * summary["implausible_count"] / summary["row_count"]

    cadence = (
        data.sort_values(keys + ["obs_time"])
        .groupby(keys, dropna=False)["obs_time"]
        .apply(lambda x: x.drop_duplicates().diff().dt.total_seconds().div(3600).median())
        .rename("median_interval_hours")
        .reset_index()
    )
    summary = summary.merge(cadence, on=keys, how="left")
    return data, summary


def mapping_matrix(profile: pd.DataFrame) -> pd.DataFrame:
    """Summarize source availability for every station/canonical variable."""
    if profile.empty:
        return pd.DataFrame()
    text = profile.assign(
        candidate=profile["net_var_name"]
        + " ["
        + profile["source_family"]
        + ", p"
        + profile["priority"].astype(str)
        + "]"
    )
    matrix = (
        text.groupby(["station_id", "canonical_variable"])["candidate"]
        .agg(lambda values: "; ".join(dict.fromkeys(values)))
        .unstack(fill_value="NOT AVAILABLE")
    )
    return matrix.reindex(columns=CANONICAL_VARIABLES, fill_value="NOT AVAILABLE")


def overlap_comparison(
    observations: pd.DataFrame,
    station_id: int,
    vars_id_a: int,
    vars_id_b: int,
) -> tuple[pd.DataFrame, dict]:
    """Compare two sources at exact overlapping timestamps."""
    subset = observations[
        (observations["station_id"] == station_id)
        & observations["vars_id"].isin([vars_id_a, vars_id_b])
    ]
    wide = subset.pivot_table(index="obs_time", columns="vars_id", values="datum", aggfunc="first")
    if vars_id_a not in wide or vars_id_b not in wide:
        return pd.DataFrame(), {"overlap_count": 0}
    paired = wide[[vars_id_a, vars_id_b]].dropna().copy()
    paired["difference"] = paired[vars_id_a] - paired[vars_id_b]
    stats = {
        "overlap_count": len(paired),
        "mean_difference": paired["difference"].mean(),
        "median_absolute_difference": paired["difference"].abs().median(),
        "correlation": paired[vars_id_a].corr(paired[vars_id_b]),
    }
    return paired, stats
