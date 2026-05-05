import numpy as np
import pandas as pd

def hourly_to_daily(df, cols, agg_map, min_hours, snwd_hour=4):
    """
    Convert hourly data to daily with validity filtering.

    snwd_hour : hour of day to extract snow depth (local time)
    """

    df = df.sort_index()

    # --- count valid values per day ---
    valid_counts = (
        df.groupby(df.index.floor("D"))[cols]
        .apply(lambda x: x.notna().sum())
    )

    # --- build validity mask ---
    if isinstance(min_hours, dict):
        valid_days = np.ones(len(valid_counts), dtype=bool)
        for c in cols:
            valid_days &= valid_counts[c] >= min_hours.get(c, 0)
        valid_days = pd.Series(valid_days, index=valid_counts.index)
    else:
        valid_days = valid_counts.ge(min_hours).all(axis=1)

    # --- normal aggregation (exclude snw_dpth for now) ---
    agg_map_clean = {k: v for k, v in agg_map.items() if k != "snw_dpth"}
    daily = df.resample("1D").agg(agg_map_clean)

    # --- handle snow depth at fixed hour ---
    if "snw_dpth" in cols:
        snwd = df["snw_dpth"].copy()

        # select values at target hour
        snwd_at_hour = snwd[snwd.index.hour == snwd_hour]

        # group by day
        snwd_daily = snwd_at_hour.groupby(snwd_at_hour.index.floor("D")).first()

        # attach to daily
        daily["snw_dpth"] = snwd_daily

    # --- apply validity mask ---
    daily = daily.where(valid_days)

    return daily




def build_daily_all(df_station):
    df_station = df_station.copy()
    df_station["obs_time"] = pd.to_datetime(df_station["obs_time"])
    df_sql = df_station.pivot_table(
        index="obs_time",
        columns="net_var_name",
        values="datum"
    ).sort_index()
    df_sql = df_sql.rename(columns={
        "min_air_temp_snc_last_reset": "tmin",
        "max_air_temp_snc_last_reset": "tmax",
        "air_temp": "temp",
        "pcpn_amt_pst1hr": "precip",
        "snwfl_amt_pst1hr": "snw_fall"
    })
    expected_cols = ["temp", "tmin", "tmax", "precip", "snw_fall", "snw_dpth"]
    df_sql = df_sql.reindex(columns=expected_cols)
    start_time = df_sql.apply(lambda col: col.first_valid_index()).min()
    if pd.isna(start_time):
        df_trim = df_sql
    else:
        df_trim = df_sql.loc[start_time:]

    daily_tas = hourly_to_daily(
        df_trim,
        cols=["tmax", "tmin", "temp"],
        agg_map={"temp": "mean", "tmax": "max", "tmin": "min"},
        min_hours=18
    )
    daily_sn = hourly_to_daily(
        df_trim,
        cols=["snw_fall", "snw_dpth"],
        agg_map={"snw_fall": "sum"},
        min_hours=18,
        snwd_hour=4
    )
    daily_precip = hourly_to_daily(
        df_trim,
        cols=["precip"],
        agg_map={"precip": "sum"},
        min_hours=18
    )
    return pd.concat([daily_tas, daily_precip, daily_sn], axis=1)