import pandas as pd
import numpy as np


def inttemp_snow_fall_dpth_consistency(df, snow_col="snw_fall", snwd_col="snw_dpth"):
    df = df.copy()

    SNOW = df[snow_col]
    SNWD = df[snwd_col]

    SNOW_prev = SNOW.shift(1)
    SNOW_next = SNOW.shift(-1)
    SNWD_prev = SNWD.shift(1)

    snwd_change = SNWD - SNWD_prev

    # -------------------------------------------------
    # 1. validity masks (THIS is the key improvement)
    # -------------------------------------------------
    valid_prev = SNOW.notna() & SNOW_prev.notna() & SNWD.notna() & SNWD_prev.notna()
    valid_next = SNOW.notna() & SNOW_next.notna() & SNWD.notna() & SNWD_prev.notna()

    valid_any = valid_prev | valid_next

    # -------------------------------------------------
    # 2. conditions (only computed where valid)
    # -------------------------------------------------
    cond_prev = snwd_change > (SNOW + SNOW_prev + 25)
    cond_next = snwd_change > (SNOW + SNOW_next + 25)

    flag_raw = cond_prev | cond_next

    # -------------------------------------------------
    # 3. final flag WITH explicit missing
    # -------------------------------------------------
    flag = flag_raw.where(valid_any, pd.NA)

    # -------------------------------------------------
    # 4. output
    # -------------------------------------------------
    flags = pd.DataFrame(index=df.index)

    flags["flag_snow_snwd"] = flag

    # shift preserves NA automatically
    flags["flag_snwd_prev"] = flag.shift(-1)

    # optional: explicitly mark missing source data
    flags["flag_missing_input"] = (~valid_any).astype("Int64")

    return flags
