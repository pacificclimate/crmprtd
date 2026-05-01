import pandas as pd
import numpy as np


def inttemp_snow_precip_consistency(
    df,
    snow_col="snw_fall",
    snwd_col="snw_dpth",
    prcp_col="precip",
    snow_thresh1=100,
    snow_thresh2=200,
    snwd_thresh1=100,
    snwd_thresh2=200
):

    df = df.copy()

    SNOW = df[snow_col]
    SNWD = df[snwd_col]
    PRCP = df[prcp_col]

    SNOW_prev = SNOW.shift(1)
    SNOW_next = SNOW.shift(-1)

    SNWD_prev = SNWD.shift(1)
    snwd_change = SNWD - SNWD_prev

    PRCP_prev = PRCP.shift(1)
    PRCP_next = PRCP.shift(-1)

    prcp_window_max = pd.concat(
        [PRCP_prev, PRCP, PRCP_next], axis=1
    ).max(axis=1)

    valid_prcp = PRCP.notna() & (
        PRCP_prev.notna() | PRCP_next.notna()
    )

    # print((PRCP.isna()).mean())
    # print((PRCP.shift(1).isna()).mean())
    # print((PRCP.shift(-1).isna()).mean())

    # print(valid_rate)

    # print(df["snw_fall"].describe())
    # print((df["snw_dpth"].diff()).describe())

    # -------------------------------------------------
    # 1. validity masks (STRICT like other functions)
    # -------------------------------------------------
    valid_snow = SNOW.notna()
    valid_prcp = PRCP.notna() & PRCP_prev.notna() & PRCP_next.notna()
    valid_snwd = SNWD.notna() & SNWD_prev.notna()

    # combine per-variable validity
    valid_snow_prcp = valid_snow & valid_prcp
    valid_snwd_prcp = valid_snwd & valid_prcp

    # -------------------------------------------------
    # 2. conditions (compute everywhere first)
    # -------------------------------------------------
    cond_snow_no_prcp = (SNOW >= snow_thresh1) & (prcp_window_max == 0)
    cond_prev = SNOW >= snow_thresh1 * (PRCP + PRCP_prev)
    cond_next = SNOW >= snow_thresh1 * (PRCP + PRCP_next)

    cond_prev_snwd = snwd_change >= snwd_thresh1 * (PRCP + PRCP_prev)
    cond_next_snwd = snwd_change >= snwd_thresh1 * (PRCP + PRCP_next)

    cond_snow_ratio = (
        (SNOW >= snow_thresh2) &
        (cond_prev | cond_next)
    )

    cond_snwd_no_prcp = (
        (snwd_change >= snwd_thresh1) &
        (prcp_window_max == 0)
    )

    cond_snwd_ratio = (
        (snwd_change >= snwd_thresh2) &
        (cond_prev_snwd & cond_next_snwd)
    )

    # -------------------------------------------------
    # 3. apply validity → explicit NA
    # -------------------------------------------------
    flag_snow_no_prcp = cond_snow_no_prcp.where(valid_snow_prcp, pd.NA)
    flag_snow_prcp_ratio = cond_snow_ratio.where(valid_snow_prcp, pd.NA)

    flag_snwd_no_prcp = cond_snwd_no_prcp.where(valid_snwd_prcp, pd.NA)
    flag_snwd_prcp_ratio = cond_snwd_ratio.where(valid_snwd_prcp, pd.NA)

    # -------------------------------------------------
    # 4. combine flags (preserve NA properly)
    # -------------------------------------------------
    def combine_flags(*args):
        out = args[0]
        for a in args[1:]:
            out = out | a
        return out

    flag_snow = combine_flags(flag_snow_no_prcp, flag_snow_prcp_ratio)
    flag_snwd = combine_flags(flag_snwd_no_prcp, flag_snwd_prcp_ratio)
    flag_prcp = combine_flags(
        flag_snow_no_prcp,
        flag_snow_prcp_ratio,
        flag_snwd_no_prcp,
        flag_snwd_prcp_ratio
    )

    # -------------------------------------------------
    # 5. assemble output
    # -------------------------------------------------
    flags = pd.DataFrame(index=df.index)

    flags["flag_snow_no_prcp"] = flag_snow_no_prcp
    flags["flag_snow_prcp_ratio"] = flag_snow_prcp_ratio
    flags["flag_snwd_no_prcp"] = flag_snwd_no_prcp
    flags["flag_snwd_prcp_ratio"] = flag_snwd_prcp_ratio

    flags["flag_snow"] = flag_snow
    flags["flag_snwd"] = flag_snwd
    flags["flag_prcp"] = flag_prcp

    flags["flag_snwd_prev"] = flag_snwd.shift(-1)

    # -------------------------------------------------
    # 6. explicit missing indicators (NEW)
    # -------------------------------------------------
    flags["flag_missing_snow"] = (~valid_snow).astype("Int64")
    flags["flag_missing_prcp"] = (~valid_prcp).astype("Int64")
    flags["flag_missing_snwd"] = (~valid_snwd).astype("Int64")

    flags["flag_missing_any"] = (
        (~valid_snow) | (~valid_prcp) | (~valid_snwd)
    ).astype("Int64")

    return flags
