import pandas as pd
import numpy as np


def detect_freq(index):
    dt = index.to_series().diff().dropna()
    return dt.mode()[0]

import pandas as pd
import numpy as np

def check_missing_timestamps(df, freq=None, return_full=False):
    """
    Detect missing timestamps in a time series.

    Parameters
    ----------
    df : pd.DataFrame or pd.Series
        Must have DatetimeIndex
    freq : str or pd.Timedelta, optional
        If None → automatically detected
    return_full : bool
        If True, return reindexed dataframe

    Returns
    -------
    dict with:
        - freq
        - n_missing
        - missing_pct
        - missing_times
        - (optional) df_full
    """

    # --- ensure Series ---
    if isinstance(df, pd.DataFrame):
        series = df.iloc[:, 0]
    else:
        series = df

    # --- detect frequency if not provided ---
    if freq is None:
        dt = series.index.to_series().diff().dropna()
        freq = dt.mode()[0]

    # --- build full timeline ---
    full_time = pd.date_range(
        start=series.index.min(),
        end=series.index.max(),
        freq=freq
    )

    # --- reindex ---
    df_full = series.reindex(full_time)

    # --- missing ---
    missing_mask = df_full.isna()
    missing_times = df_full.index[missing_mask]

    n_missing = missing_mask.sum()
    missing_pct = n_missing / len(full_time) * 100

    # --- output ---
    result = {
        "freq": freq,
        "n_missing": int(n_missing),
        "missing_pct": missing_pct,
        "missing_times": missing_times
    }

    if return_full:
        result["df_full"] = df_full

    return result
    
def qc_range_check(df, min_val=-20, max_val=20):
    """
    Quality control for threshold exceedance.

    Parameters
    ----------
    df : pd.DataFrame (time index, single column)
    min_val, max_val : float
        valid range

    Returns
    -------
    dict with:
        flag : 0/1 (out-of-range)
        deviation : distance from threshold
    """

    x = df.copy()

    # --- flag ---
    flag = ((x > max_val) | (x < min_val)).astype(int)

    # --- deviation (distance from nearest bound) ---
    deviation = x.copy().astype(float)

    deviation[x > max_val] = x[x > max_val] - max_val
    deviation[x < min_val] = min_val - x[x < min_val]
    deviation[(x >= min_val) & (x <= max_val)] = 0

    return {
        "flag": flag,
        "deviation": deviation
    }