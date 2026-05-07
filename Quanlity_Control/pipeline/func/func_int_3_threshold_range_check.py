import pandas as pd
import numpy as np


def qc_range_check(df, value_col, min_val, max_val):
    """
    Quality control for threshold exceedance.
    """

    # --- get series ---
    if value_col is None:
        x = df.iloc[:, 0]
    else:
        x = df[value_col]

    # --------------------------
    # flag logic (robust)
    # --------------------------
    flag = pd.Series(False, index=x.index)

    if max_val is not None:
        flag |= (x > max_val)

    if min_val is not None:
        flag |= (x < min_val)

    flag = flag.astype(int)

    # --------------------------
    # deviation
    # --------------------------
    deviation = pd.Series(0.0, index=x.index)

    if max_val is not None:
        deviation[x > max_val] = x[x > max_val] - max_val

    if min_val is not None:
        deviation[x < min_val] = min_val - x[x < min_val]

    # --------------------------
    # NEW: negative flag (only for relevant vars)
    # --------------------------
    neg_flag = None

    if value_col in ["precip", "snw_fall", "snw_dpth"]:
        neg_flag = x < 0

    # --------------------------
    # return
    # --------------------------
    return {
        "flag": flag,
        "neg_flag": neg_flag,
        "deviation": deviation
    }