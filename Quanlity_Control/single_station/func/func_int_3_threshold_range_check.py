import pandas as pd
import numpy as np


def qc_range_check(df, value_col, min_val, max_val):
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

    if value_col is None:
        x = df.iloc[:, 0]
    else:
        x = df[value_col]

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

