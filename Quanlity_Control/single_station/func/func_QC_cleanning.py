import pandas as pd
import numpy as np


def apply_qc_cleaning(
    daily_all,
    range_flags,
    naught_result,
    dup_result_dict,
    ind_result_dict,
    value_cols
):
    """
    Apply QC cleaning rules to daily dataset.

    Parameters
    ----------
    daily_all : pd.DataFrame
        Original daily data
    range_flags : pd.DataFrame
        Range QC flags (1 = bad)
    naught_result : dict or DataFrame
        Trace/zero flags
    dup_result_dict : dict
        Duplicate / flatline detection results
    ind_result_dict : dict
        Independence / streak detection results
    value_cols : list
        Variables to apply streak filtering

    Returns
    -------
    pd.DataFrame
        Cleaned dataset
    """

    daily_cleaned = daily_all.copy()

    # --------------------------------------------------
    # 1. Negative values → 0
    # --------------------------------------------------
    for var in ["precip", "snw_fall", "snw_dpth"]:
        if var in daily_cleaned.columns:
            daily_cleaned.loc[daily_cleaned[var] < 0, var] = 0

    # --------------------------------------------------
    # 2. Range flags → NaN
    # --------------------------------------------------
    for var in range_flags.columns:
        if var in daily_cleaned.columns:
            mask = range_flags[var] == 1
            daily_cleaned.loc[mask, var] = np.nan

    # --------------------------------------------------
    # 3. Trace / zero flags → NaN
    # --------------------------------------------------
    naught_var_map = {
        "temp": "temp_zero",
        "tmin": "tmin_zero",
        "tmax": "tmax_zero",
        "precip": "precip_trace",
        "snw_fall": "snw_fall_trace",
        "snw_dpth": "snw_dpth_trace",
    }

    for var, flag_col in naught_var_map.items():
        if var in daily_cleaned.columns and flag_col in naught_result:
            flag_series = naught_result[flag_col]

            if isinstance(flag_series, pd.DataFrame):
                flag_series = flag_series.iloc[:, 0]

            daily_cleaned.loc[flag_series == True, var] = np.nan

    # --------------------------------------------------
    # 4. Flatline / duplicate Tmin-Tmax → NaN
    # --------------------------------------------------
    for var in ["tmin", "tmax"]:
        if var in dup_result_dict:
            flatline_flags = dup_result_dict[var].get("tmin_tmax_equal")

            if flatline_flags is not None:
                for flag_col in ["flag_tmax_tmin_equal", "flag_month_flatline"]:
                    if flag_col in flatline_flags.columns:
                        mask = flatline_flags[flag_col] == True
                        daily_cleaned.loc[mask, ["tmin", "tmax"]] = np.nan

    # --------------------------------------------------
    # 5. Streak removal → NaN
    # --------------------------------------------------
    for var in value_cols:
        if var not in daily_cleaned.columns:
            continue

        streaks = ind_result_dict.get(var, {}).get("streaks", [])
        if not streaks:
            continue

        streak_mask = pd.Series(False, index=daily_cleaned.index)

        for start, end, _ in streaks:
            streak_mask |= (
                (daily_cleaned.index >= pd.to_datetime(start)) &
                (daily_cleaned.index <= pd.to_datetime(end))
            )

        daily_cleaned.loc[streak_mask, var] = np.nan

    return daily_cleaned


import pandas as pd
import numpy as np

def apply_inttemp_tas_qc(daily_cleaned, inttemp_tas_result):
    """
    Remove inttemp_tas values where qc_label == 'bad'

    Parameters
    ----------
    daily_cleaned : pd.DataFrame
        Data to clean (will not be modified in-place)
    inttemp_tas_result : dict or pd.DataFrame
        Contains 'qc_label' column/series

    Returns
    -------
    pd.DataFrame
        Updated DataFrame
    """

    df = daily_cleaned.copy()

    if "inttemp_tas" in df.columns:

        # handle dict or DataFrame input
        qc_series = (
            inttemp_tas_result.get("qc_label")
            if isinstance(inttemp_tas_result, dict)
            else inttemp_tas_result["qc_label"]
            if "qc_label" in inttemp_tas_result
            else None
        )

        if qc_series is not None:
            qc_series = qc_series.reindex(df.index)

            mask = qc_series == "bad"
            df.loc[mask, "inttemp_tas"] = np.nan

    return df