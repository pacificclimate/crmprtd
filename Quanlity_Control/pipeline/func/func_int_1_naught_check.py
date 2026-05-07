import pandas as pd
import numpy as np

def qc_temperature_zero_check(df,
                              tmax_col="tmax",
                              tmin_col="tmin"):
    """
    Detect suspicious temperature coding:
    - 0°C / 0°C
    - -17.8°C / -17.8°C (0°F)
    """

    df = df.copy()

    tmax = df[tmax_col]
    tmin = df[tmin_col]

    flag = (
        ((tmax == 0) & (tmin == 0)) |
        ((tmax == -17.8) & (tmin == -17.8))
    )

    return pd.DataFrame({
        "flag_temp_naught": flag
    })

    
# def qc_temperature_zero_check(df,
#                               tmax_col="tmax",
#                               tmin_col="tmin",
#                               us_flag=None):
#     """
#     Detect suspicious zero / -17.8°C temperature coding.
    
#     Parameters
#     ----------
#     us_flag : pd.Series or None
#         Boolean series indicating US stations.
#         If None → assume non-US rule (0°C check)
#     """

#     df = df.copy()

#     tmax = df[tmax_col]
#     tmin = df[tmin_col]

#     # --------------------------
#     # US stations rule
#     # --------------------------
#     if us_flag is not None:
#         flag_us = (
#             (tmax == -17.8) &
#             (tmin == -17.8)
#         )

#         flag_non_us = (
#             (tmax == 0) &
#             (tmin == 0)
#         )

#         flag = flag_us.where(us_flag, flag_non_us)

#     # --------------------------
#     # default rule (no metadata)
#     # --------------------------
#     else:
#         flag = (
#             (tmax == 0) &
#             (tmin == 0)
#         )

#     return pd.DataFrame({
#         "flag_temp_naught": flag
#     })


def qc_trace_values(df,
                    value_col,
                    flag_col="qflag"):
    """
    Detect trace values (QC flag = 'T')
    """

    df = df.copy()

    value = df[value_col]

    # if QC flag column exists
    if flag_col not in df.columns:
        return pd.DataFrame({
            f"flag_{value_col}_trace": pd.Series(False, index=df.index)
        })

    qc_flag = df[flag_col]

    flag = (
        (qc_flag == "T") &
        (value > 0) &
        (value.notna())
    )

    return pd.DataFrame({
        f"flag_{value_col}_trace": flag
    })


def qc_naught_and_trace(df):

    result = {}

    # temperature zeros
    # trace variables
    for col in ["temp", "tmin", "tmax"]:
        if col in df.columns:
            result[f"{col}"] = qc_temperature_zero_check(df)

    # trace variables
    for col in ["precip", "snw_fall", "snw_dpth"]:
        if col in df.columns:
            result[f"{col}"] = qc_trace_values(df, col)

    return result