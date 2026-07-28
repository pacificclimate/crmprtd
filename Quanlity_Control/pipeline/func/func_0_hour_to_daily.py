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
        thresholds = pd.Series(
            {column: min_hours.get(column, 0) for column in cols}
        )
        valid_days = valid_counts[cols].ge(thresholds, axis="columns")
    else:
        valid_days = valid_counts[cols].ge(min_hours)

    # --- normal aggregation (exclude snw_dpth for now) ---
    agg_map_clean = {k: v for k, v in agg_map.items() if k != "snw_dpth"}
    daily = df.resample("1D").agg(agg_map_clean)
    daily = daily.where(valid_days.reindex(columns=daily.columns, fill_value=False))

    # --- handle snow depth at fixed hour ---
    if "snw_dpth" in cols:
        snwd = df["snw_dpth"].copy()

        # select values at target hour
        snwd_at_hour = snwd[snwd.index.hour == snwd_hour]

        # group by day
        snwd_daily = snwd_at_hour.groupby(snwd_at_hour.index.floor("D")).first()

        # attach to daily
        daily["snw_dpth"] = snwd_daily.where(valid_days["snw_dpth"])

    # --- apply validity mask ---
    daily = daily.where(valid_days)

    return daily




def build_daily_all(df_station, variable_frequencies=None):
    """Build daily QC inputs from a mixture of hourly and daily sources.

    Parameters
    ----------
    df_station : DataFrame
        Long-form observations with ``obs_time``, ``net_var_name``, and
        ``datum`` columns.
    variable_frequencies : dict, optional
        QC variable names mapped to ``"hourly"`` or ``"daily"``. Variables
        not listed are treated as hourly for backward compatibility.
    """
    variable_frequencies = variable_frequencies or {}
    invalid_frequencies = {
        variable: frequency
        for variable, frequency in variable_frequencies.items()
        if frequency not in {"hourly", "daily"}
    }
    if invalid_frequencies:
        raise ValueError(
            f"Unsupported variable frequencies: {invalid_frequencies}"
        )

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
    first_valid_times = [
        column.first_valid_index()
        for _, column in df_sql.items()
        if column.first_valid_index() is not None
    ]
    if not first_valid_times:
        df_trim = df_sql
    else:
        start_time = min(first_valid_times)
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
    daily = pd.concat([daily_tas, daily_precip, daily_sn], axis=1)

    # Daily source values have already undergone their source aggregation.
    # Preserve them without applying the hourly 18-observation requirement.
    for variable, frequency in variable_frequencies.items():
        if frequency != "daily" or variable not in df_trim.columns:
            continue
        # The value already represents a daily statistic or accumulation, so
        # do not apply min/max/sum again. ``first`` also preserves NaN for a
        # day with no reported value instead of turning a missing sum into 0.
        daily[variable] = df_trim[variable].resample("1D").first()

    return daily.reindex(columns=expected_cols).sort_index()
