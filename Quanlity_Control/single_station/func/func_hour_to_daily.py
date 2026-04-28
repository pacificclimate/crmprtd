import numpy as np


def hourly_to_daily(df, cols, agg_map, min_hours):
    """
    Convert hourly data to daily with validity filtering.

    df        : DataFrame with datetime index
    cols      : columns to check for validity
    agg_map   : dict of aggregation rules
    min_hours : minimum valid hourly observations per day
                (int or dict per column)
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

    # --- aggregate ---
    daily = df.resample("1D").agg(agg_map)

    # --- apply mask ---
    daily = daily.where(valid_days)

    return daily
