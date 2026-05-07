import pandas as pd
import numpy as np

from crmprtd import setup_logging
from func_0_hour_to_daily import hourly_to_daily, build_daily_all
from func_int_1_naught_check import qc_naught_and_trace
from func_int_5_missing_check import check_missing_timestamps
from func_int_2_dunplicate_check import duplicate_check
from func_int_4_identical_value_streak_check import identify_value_streaks
from func_int_3_threshold_range_check import qc_range_check
from func_clim_1_gap_check import gap_check_two_tailed, gap_check_one_tailed
from func_clim_2_climatological_outlier_checks import temp_outlier_flags, precip_outlier_flags
from func_inttemp_1_tas_check import inttemp_temperature_consistency
from func_inttemp_2_snow_tmin_check import inttemp_snow_temp_consistency
from func_inttemp_3_snow_fall_dpth_check import inttemp_snow_fall_dpth_consistency
from func_inttempt_4_snow_precipitation_check import inttemp_snow_precip_consistency
from func_QC_cleanning import apply_qc_cleaning, apply_inttemp_tas_qc
from func_station_quality_evaluation import (
    # summarize_flagged_values,
    evaluate_station_quality,
    get_station_rating
)

from func_analyze_temporal_coverage import analyze_temporal_coverage


def run_qc_result_pipeline(daily_all, value_cols):

    # --------------------------------------------------
    # 1. Detect trace / zero values (instrument-level flags)
    # --------------------------------------------------
    naught_result = qc_naught_and_trace(daily_all)

    # Combine all naught results into a single DataFrame
    # (each variable becomes one column)
    naught_all = pd.concat([
        df.rename(columns={df.columns[0]: name}) if isinstance(
            df, pd.DataFrame) and len(df.columns) == 1 else df.to_frame(name=name)
        for name, df in naught_result.items()
    ], axis=1)

    # --------------------------------------------------
    # 2. Missing data detection (temporal completeness)
    # --------------------------------------------------
    miss_result_dict = {
        col: check_missing_timestamps(daily_all, value_col=col)
        for col in value_cols
    }

    # --------------------------------------------------
    # 3. Duplicate / flatline detection
    # (e.g., constant values, Tmin = Tmax issues)
    # --------------------------------------------------
    dup_result_dict = {
        col: duplicate_check(daily_all, value_col=col)
        for col in value_cols
    }

    # --------------------------------------------------
    # 4. WMO-based physical range checks
    # (define physically plausible limits)
    # --------------------------------------------------
    wmo_rules = {
        "temp": {"min": -89.4, "max": 57.7},
        "tmin": {"min": -89.4, "max": 57.7},
        "tmax": {"min": -89.4, "max": 57.7},
        "precip": {"min": None, "max": 400},
        "snw_fall": {"min": None, "max": 1925},
        "snw_dpth": {"min": None, "max": 11460},
    }

    # Apply range check per variable
    range_results = {}
    for var, bounds in wmo_rules.items():
        if var not in daily_all.columns:
            continue

        range_results[var] = qc_range_check(
            daily_all,
            value_col=var,
            min_val=bounds["min"],
            max_val=bounds["max"]
        )

        # Combine all flags into one DataFrame
        range_flags = pd.concat(
            {var: res["flag"] for var, res in range_results.items()},
            axis=1
        )

    # --------------------------------------------------
    # 5. Detect suspicious streaks (e.g., repeated values)
    # --------------------------------------------------
    ind_result_dict = {
        col: identify_value_streaks(daily_all, value_col=col)
        for col in value_cols
    }

    # --------------------------------------------------
    # 6. Apply core QC cleaning (set bad values → NaN)
    # --------------------------------------------------
    daily_cleaned = apply_qc_cleaning(
        daily_all=daily_all,
        range_flags=range_flags,
        naught_result=naught_result,
        dup_result_dict=dup_result_dict,
        ind_result_dict=ind_result_dict,
        value_cols=value_cols
    )

    # --------------------------------------------------
    # 7. Gap check (detect sudden unrealistic jumps)
    # --------------------------------------------------
    gap_threshold = {
        "temp": 10,
        "tmin": 10,
        "tmax": 10,
        "precip": 300,
        "snw_dpth": 350
    }

    gap_result_dict = {}
    for col, thresh in gap_threshold.items():
        if col not in daily_cleaned.columns:
            continue

        # Use two-tailed for temperature-like variables
        if col in ["temp", "tmin", "tmax", "snw_dpth"]:
            gap_result_dict[col] = gap_check_two_tailed(
                daily_cleaned, col, thresh
            )
        else:
            # One-tailed for precipitation
            gap_result_dict[col] = gap_check_one_tailed(
                daily_cleaned, col, thresh
            )

    # --------------------------------------------------
    # 8. Climatological outlier detection
    # (based on distribution, e.g., z-score or percentiles)
    # --------------------------------------------------
    clim_flags = {}

    for var in ["temp", "tmin", "tmax"]:
        if var in daily_cleaned.columns:
            clim_flags[var] = temp_outlier_flags(
                daily_cleaned, var, z_threshold=6
            )

    if "precip" in daily_cleaned.columns:
        clim_flags["precip"] = precip_outlier_flags(
            daily_cleaned, per_threshold=9
        )

    # Combine climatology flags
    clim_flag_df = (
        pd.concat(clim_flags.values(), axis=1)
        if clim_flags else
        pd.DataFrame(index=daily_cleaned.index)
    )

    # --------------------------------------------------
    # 9. Internal consistency checks (cross-variable logic)
    # --------------------------------------------------
    inttemp_tas_result = inttemp_temperature_consistency(daily_cleaned)

    # Apply QC removal for bad internal consistency
    daily_cleaned_final = apply_inttemp_tas_qc(
        daily_cleaned, inttemp_tas_result
    )

    # Additional consistency checks
    inttemp_snow_tmin_result = inttemp_snow_temp_consistency(daily_cleaned_final)
    inttemp_snow_fall_dpth_result = inttemp_snow_fall_dpth_consistency(daily_cleaned_final)
    inttemp_snow_precip_result = inttemp_snow_precip_consistency(daily_cleaned_final)



    # --------------------------------------------------
    # Return all outputs for further analysis / plotting
    # --------------------------------------------------
    return {
        "daily_cleaned": daily_cleaned_final,
        "daily_cleaned_half": daily_cleaned,
        "naught_result": naught_result,
        "naught_all": naught_all,
        "miss_result_dict": miss_result_dict,
        "dup_result_dict": dup_result_dict,
        "ind_result_dict": ind_result_dict,
        "range_results": range_results,
        "gap_result_dict": gap_result_dict,
        "clim_flag_df": clim_flag_df,
        "wmo_rules": wmo_rules,
        "inttemp_tas_result": inttemp_tas_result,
        "inttemp_snow_tmin_result": inttemp_snow_tmin_result,
        "inttemp_snow_fall_dpth_result": inttemp_snow_fall_dpth_result,
        "inttemp_snow_precip_result": inttemp_snow_precip_result,
    }