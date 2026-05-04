import numpy as np

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