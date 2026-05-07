import pandas as pd


def inttemp_snow_temp_consistency(df,
                 snow_col="snw_fall",
                 snwd_col="snw_dpth",
                 tmin_col="tmin"):

    df = df.copy()

    SNOW = df[snow_col]
    SNWD = df[snwd_col]
    TMIN = df[tmin_col]

    TMIN_prev = TMIN.shift(1)
    TMIN_next = TMIN.shift(-1)
    SNWD_prev = SNWD.shift(1)

    # -------------------------------------------------
    # derived variables
    # -------------------------------------------------
    tmin_min = pd.concat([TMIN_prev, TMIN_next], axis=1).min(axis=1)
    snwd_change = SNWD - SNWD_prev

    # -------------------------------------------------
    # 1. validity masks (like your snow_only function)
    # -------------------------------------------------
    valid_snow = SNOW.notna() & TMIN_prev.notna() & TMIN_next.notna()
    valid_snwd = SNWD.notna() & SNWD_prev.notna(
    ) & TMIN_prev.notna() & TMIN_next.notna()

    # -------------------------------------------------
    # 2. conditions (compute everywhere first)
    # -------------------------------------------------
    cond_snow = (SNOW > 0) & (tmin_min >= 7)
    cond_snwd = (snwd_change > 0) & (tmin_min >= 7)

    # -------------------------------------------------
    # 3. apply validity → explicit NA
    # -------------------------------------------------
    flag_snow_warm = cond_snow.where(valid_snow, pd.NA)
    flag_snwd_warm = cond_snwd.where(valid_snwd, pd.NA)

    # -------------------------------------------------
    # 4. output
    # -------------------------------------------------
    flags = pd.DataFrame(index=df.index)

    flags["flag_snow_warm"] = flag_snow_warm
    flags["flag_snwd_warm"] = flag_snwd_warm

    # propagate to previous day (consistent with your design)
    flags["flag_snwd_warm_prev"] = flag_snwd_warm.shift(-1)

    # -------------------------------------------------
    # 5. explicit missing indicators (VERY useful)
    # -------------------------------------------------
    flags["flag_missing_snow"] = (~valid_snow).astype("Int64")
    flags["flag_missing_snwd"] = (~valid_snwd).astype("Int64")

    # combined missing (optional but convenient)
    flags["flag_missing_any"] = ((~valid_snow) | (~valid_snwd)).astype("Int64")

    return flags