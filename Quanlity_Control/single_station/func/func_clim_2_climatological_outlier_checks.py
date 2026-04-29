import numpy as np
import pandas as pd
from astropy.stats import biweight_location, biweight_scale


def temp_outlier_flags(df, value_col, z_threshold = 6):

    df = df.copy()
    df["doy"] = df.index.dayofyear
    df.loc[df["doy"] == 366, "doy"] = 365

    mu_arr = np.full(len(df), np.nan)
    sigma_arr = np.full(len(df), np.nan)

    for doy in range(1, 366):

        window = [(doy + d - 1) % 365 + 1 for d in range(-7, 8)]

        mask_window = df["doy"].isin(window)
        clim = df.loc[mask_window, value_col].dropna().values

        if len(clim) < 100:
            continue

        mu = biweight_location(clim)
        sigma = biweight_scale(clim)

        if sigma == 0 or np.isnan(sigma):
            continue

        mask_target = df["doy"] == doy
        mu_arr[mask_target] = mu
        sigma_arr[mask_target] = sigma

    z = (df[value_col].values - mu_arr) / sigma_arr
    flags = (np.abs(z) > z_threshold) & (~np.isnan(z))

    return pd.Series(flags, index=df.index, name=f"{value_col}")

def precip_outlier_flags(df, per_threshold = 9):

    df = df.copy()
    df["doy"] = df.index.dayofyear
    df.loc[df["doy"] == 366, "doy"] = 365

    p95_arr = np.full(len(df), np.nan)

    for doy in range(1, 366):

        window = [(doy + d - 1) % 365 + 1 for d in range(-14, 15)]

        mask_window = df["doy"].isin(window)
        clim = df.loc[mask_window, "precip"]
        clim = clim[clim > 0]

        if len(clim) < 20:
            continue

        p95 = np.percentile(clim, 95)

        mask_target = df["doy"] == doy
        p95_arr[mask_target] = p95

    # -------------------------
    # base rule
    # -------------------------
    threshold_base = per_threshold * p95_arr

    flag_base = df["precip"].values >= threshold_base

    # -------------------------
    # NEW RULE (important)
    # -------------------------
    if {"tmin", "tmax"}.issubset(df.columns):

        tmean = 0.5 * (df["tmax"].values + df["tmin"].values)

        flag_cold_extreme = (
            (df["precip"].values >= 5 * p95_arr) &
            (tmean < 0)
        )
    else:
        flag_cold_extreme = np.zeros(len(df), dtype=bool)

    # combine
    flags = flag_base | flag_cold_extreme

    return pd.Series(flags, index=df.index, name="precip")