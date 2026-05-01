import pandas as pd
import numpy as np


def inttemp_temperature_consistency(
    df,
    tmax_col="tmax",
    tmin_col="tmin",
    tobs_col="temp",
    spike_threshold=25,
    lag_threshold=40
):
    """
    Internal consistency QC for temperature observations.

    QC logic:
    ----------
    0 = missing
    1 = good
    2 = suspect (spike or lag inconsistency)
    3 = bad (physical inconsistency)

    Returns
    -------
    result : pd.DataFrame
        Original data + QC flags + qc_label + qc_code
    """

    df = df.sort_index().copy()

    # ------------------------------------------------------------
    # 1. Extract variables
    # ------------------------------------------------------------
    TMAX = df[tmax_col]
    TMIN = df[tmin_col]
    TOBS = df[tobs_col]

    # ------------------------------------------------------------
    # 2. Missing mask
    # (all variables missing)
    # ------------------------------------------------------------
    missing = TMAX.isna() & TMIN.isna() & TOBS.isna()

    # ------------------------------------------------------------
    # 3. Basic physical consistency
    # TMAX >= TOBS >= TMIN
    # ------------------------------------------------------------
    flag_basic = ~((TMAX >= TMIN) & (TMAX >= TOBS) & (TOBS >= TMIN))
    flag_basic = flag_basic & ~missing

    # ------------------------------------------------------------
    # 4. Spike / dip check
    # ------------------------------------------------------------
    flag_spike = (
        ((TMAX - TMAX.shift(1)).abs() > spike_threshold) |
        ((TMIN - TMIN.shift(1)).abs() > spike_threshold) |
        ((TOBS - TOBS.shift(1)).abs() > spike_threshold)
    )
    flag_spike = flag_spike & ~missing

    # ------------------------------------------------------------
    # 5. Lagged consistency
    # ------------------------------------------------------------
    tmax_prev_max = pd.concat(
        [TMIN.shift(1), TOBS.shift(1)], axis=1
    ).max(axis=1)

    tmin_prev_min = pd.concat(
        [TMAX.shift(1), TOBS.shift(1)], axis=1
    ).min(axis=1)

    flag_lag = (
        (TMAX < (tmax_prev_max - lag_threshold)) |
        (TMIN > (tmin_prev_min + lag_threshold))
    )
    flag_lag = flag_lag & ~missing

    # ------------------------------------------------------------
    # 6. Combine flags
    # ------------------------------------------------------------
    qc_flags = pd.DataFrame({
        "flag_missing": missing,
        "flag_basic": flag_basic,
        "flag_spike": flag_spike,
        "flag_lag": flag_lag
    }, index=df.index)

    qc_flags["flag_any"] = (
        qc_flags[["flag_basic", "flag_spike", "flag_lag"]]
        .any(axis=1)
    )

    # ------------------------------------------------------------
    # 7. QC label (human readable)
    # ------------------------------------------------------------
    qc_flags["qc_label"] = "good"

    qc_flags.loc[qc_flags["flag_missing"], "qc_label"] = "missing"

    qc_flags.loc[qc_flags["flag_basic"], "qc_label"] = "bad"

    qc_flags.loc[
        (~qc_flags["flag_missing"]) &
        (~qc_flags["flag_basic"]) &
        (qc_flags["flag_spike"] | qc_flags["flag_lag"]),
        "qc_label"
    ] = "suspect"

    # ------------------------------------------------------------
    # 8. QC code (numeric)
    # ------------------------------------------------------------
    qc_flags["qc_code"] = 1  # good

    qc_flags.loc[qc_flags["flag_missing"], "qc_code"] = 0
    qc_flags.loc[qc_flags["flag_basic"], "qc_code"] = 3
    qc_flags.loc[
        (~qc_flags["flag_missing"]) &
        (~qc_flags["flag_basic"]) &
        (qc_flags["flag_spike"] | qc_flags["flag_lag"]),
        "qc_code"
    ] = 2

    # ------------------------------------------------------------
    # 9. Merge back to data
    # ------------------------------------------------------------
    result = df.join(qc_flags)

    return result

