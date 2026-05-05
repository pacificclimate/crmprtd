import pandas as pd
import numpy as np


def summarize_flagged_values(daily_cleaned, value_cols, dup_result_dict, ind_result_dict,
                             gap_flags, clim_flag_df, inttemp_tas_result,
                             inttemp_snow_tmin_result, inttemp_snow_fall_dpth_result,
                             inttemp_snow_precip_result):
    """
    Summarize flagged values for each variable by check type.

    Parameters:
    -----------
    daily_cleaned : DataFrame
        Cleaned daily data with datetime index
    value_cols : list
        List of variable column names
    dup_result_dict : dict
        Results from duplicate checks
    ind_result_dict : dict
        Results from identical value streak checks
    gap_flags : DataFrame
        Gap check flags
    clim_flag_df : DataFrame
        Climatological outlier flags
    inttemp_tas_result : DataFrame
        Temperature consistency flags
    inttemp_snow_tmin_result : DataFrame
        Snow-temperature consistency flags
    inttemp_snow_fall_dpth_result : DataFrame
        Snowfall-snow depth consistency flags
    inttemp_snow_precip_result : DataFrame
        Snow-precipitation consistency flags

    Returns:
    --------
    summary_flags : dict
        Summary of flagged values per variable
    """
    summary_flags = {}
    total_days = len(daily_cleaned)

    for var in value_cols:
        flagged_by_check = {}

        # 1. Duplicate checks (tmin_tmax_equal for temp vars)
        if var in ["tmin", "tmax"]:
            if dup_result_dict[var].get("tmin_tmax_equal") is not None:
                flags = dup_result_dict[var]["tmin_tmax_equal"]
                flagged_by_check["duplicate_flatline"] = flags[flags["flag_month_flatline"] == True].index.tolist()

        # 2. Value-streak checks
        streaks = ind_result_dict[var]["streaks"]
        streak_dates = set()
        for start, end, val in streaks:
            streak_dates.update(pd.date_range(start, end))
        flagged_by_check["value_streaks"] = sorted(list(streak_dates))

        # 3. Gap flags
        if var in gap_flags.columns:
            flagged_by_check["gap_flags"] = gap_flags[gap_flags[var] == 1].index.tolist()

        # 4. Climatological outlier flags
        if var in clim_flag_df.columns:
            flagged_by_check["clim_outliers"] = clim_flag_df[clim_flag_df[var] == 1].index.tolist()

        # 5. Internal temporal consistency
        if var in ["temp", "tmin", "tmax"]:
            if "flag_spike" in inttemp_tas_result.columns:
                flagged_by_check["inttemp_spike"] = inttemp_tas_result[inttemp_tas_result["flag_spike"] == True].index.tolist()
            if "flag_lag" in inttemp_tas_result.columns:
                flagged_by_check["inttemp_lag"] = inttemp_tas_result[inttemp_tas_result["flag_lag"] == True].index.tolist()

        if var == "snw_fall":
            if "flag_snow_warm" in inttemp_snow_tmin_result.columns:
                flagged_by_check["snow_temp_warm"] = inttemp_snow_tmin_result[inttemp_snow_tmin_result["flag_snow_warm"] == True].index.tolist()
            if "flag_snow_snwd" in inttemp_snow_fall_dpth_result.columns:
                flagged_by_check["snow_fall_depth"] = inttemp_snow_fall_dpth_result[inttemp_snow_fall_dpth_result["flag_snow_snwd"] == True].index.tolist()
            if "flag_snow_no_prcp" in inttemp_snow_precip_result.columns:
                flagged_by_check["snow_no_precip"] = inttemp_snow_precip_result[inttemp_snow_precip_result["flag_snow_no_prcp"] == True].index.tolist()
            if "flag_snow_prcp_ratio" in inttemp_snow_precip_result.columns:
                flagged_by_check["snow_precip_ratio"] = inttemp_snow_precip_result[inttemp_snow_precip_result["flag_snow_prcp_ratio"] == True].index.tolist()

        if var == "snw_dpth":
            if "flag_snwd_warm" in inttemp_snow_tmin_result.columns:
                flagged_by_check["snwd_temp_warm"] = inttemp_snow_tmin_result[inttemp_snow_tmin_result["flag_snwd_warm"] == True].index.tolist()
            if "flag_snow_snwd" in inttemp_snow_fall_dpth_result.columns:
                flagged_by_check["snow_fall_depth"] = inttemp_snow_fall_dpth_result[inttemp_snow_fall_dpth_result["flag_snow_snwd"] == True].index.tolist()
            if "flag_snwd_no_prcp" in inttemp_snow_precip_result.columns:
                flagged_by_check["snwd_no_precip"] = inttemp_snow_precip_result[inttemp_snow_precip_result["flag_snwd_no_prcp"] == True].index.tolist()
            if "flag_snwd_prcp_ratio" in inttemp_snow_precip_result.columns:
                flagged_by_check["snwd_precip_ratio"] = inttemp_snow_precip_result[inttemp_snow_precip_result["flag_snwd_prcp_ratio"] == True].index.tolist()

        if var == "tmin":
            if "flag_snwd_warm_prev" in inttemp_snow_tmin_result.columns:
                flagged_by_check["snwd_warm_prev"] = inttemp_snow_tmin_result[inttemp_snow_tmin_result["flag_snwd_warm_prev"] == True].index.tolist()

        if var == "precip":
            if "flag_snow_no_prcp" in inttemp_snow_precip_result.columns:
                flagged_by_check["snow_no_precip"] = inttemp_snow_precip_result[inttemp_snow_precip_result["flag_snow_no_prcp"] == True].index.tolist()
            if "flag_snwd_no_prcp" in inttemp_snow_precip_result.columns:
                flagged_by_check["snwd_no_precip"] = inttemp_snow_precip_result[inttemp_snow_precip_result["flag_snwd_no_prcp"] == True].index.tolist()

        # Aggregate all flagged dates
        all_flagged = set()
        for dates in flagged_by_check.values():
            all_flagged.update(dates)

        flag_rate = (len(all_flagged) / total_days) * 100 if total_days > 0 else 0

        summary_flags[var] = {
            "total_flagged_days": len(all_flagged),
            "flag_rate_percent": flag_rate,
            "flagged_by_check": flagged_by_check,
            "all_flagged_dates": sorted(list(all_flagged))[:10]
        }

    # Print summary
    print(f"Total days in dataset: {total_days}")
    print()
    for var, info in summary_flags.items():
        print(f"{var}: {info['total_flagged_days']} flagged days ({info['flag_rate_percent']:.2f}%)")
        for check, dates in info["flagged_by_check"].items():
            if dates:
                print(f"  {check}: {len(dates)} days")
        print(f"  Sample dates: {info['all_flagged_dates'][:5]}")
        print()

    return summary_flags


def analyze_temporal_coverage(daily_cleaned, value_cols, miss_result_dict):
    """
    Perform temporal coverage analysis including continuity, large gaps, and completeness by year.

    Parameters:
    -----------
    daily_cleaned : DataFrame
        Cleaned daily data
    value_cols : list
        Variable columns
    miss_result_dict : dict
        Missing check results

    Returns:
    --------
    completeness_by_year : dict
        Completeness data by year and variable
    """
    print("=" * 70)
    print("TEMPORAL COVERAGE ANALYSIS")
    print("=" * 70)
    print()

    # 1. Overall dataset coverage
    start_date = daily_cleaned.index.min()
    end_date = daily_cleaned.index.max()
    total_span = (end_date - start_date).days + 1

    print(f"Dataset period: {start_date.date()} to {end_date.date()}")
    print(f"Total span: {total_span} days (~{total_span/365.25:.2f} years)")
    print()

    # 2. Years covered
    years_covered = daily_cleaned.index.year.unique()
    years_covered = sorted(years_covered)
    n_years = len(years_covered)

    print(f"Years covered: {years_covered[0]} to {years_covered[-1]} ({n_years} years)")
    print()

    # 3. Continuous years check
    year_gaps = []
    for i in range(len(years_covered) - 1):
        if years_covered[i + 1] - years_covered[i] > 1:
            year_gaps.append((years_covered[i], years_covered[i + 1]))

    if year_gaps:
        print("❌ Data is NOT continuous (yearly gaps detected):")
        for y1, y2 in year_gaps:
            print(f"  - Gap between {y1} and {y2} ({y2 - y1} years missing)")
    else:
        print("✅ Continuous years: All years from", years_covered[0], "to", years_covered[-1], "are covered")
    print()

    # 4. Large gaps (> 1 year) analysis by variable
    print("Large gaps check (> 1 year = 365 days):")
    print("-" * 70)

    for var in value_cols:
        if var not in daily_cleaned.columns:
            continue

        valid_data = daily_cleaned[var].dropna()

        if len(valid_data) == 0:
            print(f"{var}: No valid data")
            continue

        valid_dates = valid_data.index.tolist()
        gaps = []

        for i in range(len(valid_dates) - 1):
            gap_days = (valid_dates[i + 1] - valid_dates[i]).days
            if gap_days > 365:
                gaps.append({
                    "start_date": valid_dates[i],
                    "end_date": valid_dates[i + 1],
                    "gap_days": gap_days,
                    "gap_years": gap_days / 365.25
                })

        if gaps:
            print(f"{var}: ⚠️ {len(gaps)} large gap(s) detected")
            for gap in gaps:
                print(f"  - {gap['start_date'].date()} → {gap['end_date'].date()}: {gap['gap_days']} days ({gap['gap_years']:.1f} years)")
        else:
            print(f"{var}: ✅ No large gaps (all gaps < 1 year)")

    print()

    # 5. Data completeness by year and variable
    print("=" * 70)
    print("DATA COMPLETENESS BY YEAR AND VARIABLE")
    print("=" * 70)
    print()

    full_index = pd.date_range(start=daily_cleaned.index.min(), end=daily_cleaned.index.max(), freq='D')

    # For snow variables, use snow season periods from missing check
    completeness_by_year = {}

    for year in years_covered:
        completeness_by_year[year] = {"total_days": 0}

        year_mask = full_index.year == year

        for var in value_cols:
            if var not in daily_cleaned.columns:
                continue

            eval_mask = year_mask.copy()
            if var in ["snw_fall", "snw_dpth"]:
                # Use snow period totals from missing check
                snow_summary = miss_result_dict[var].get("snow_period_summary", {})
                if year in snow_summary:
                    snow_days = snow_summary[year]["snow_period_days"]
                    completeness_by_year[year][var] = {
                        "valid_days": snow_days - miss_result_dict[var].get("snow_period_missing_days", 0),
                        "completeness_pct": (snow_days - miss_result_dict[var].get("snow_period_missing_days", 0)) / snow_days * 100 if snow_days > 0 else 0,
                        "total_eval_days": snow_days
                    }
                else:
                    completeness_by_year[year][var] = {"valid_days": 0, "completeness_pct": 0, "total_eval_days": 0}
            else:
                total_days = eval_mask.sum()
                series_full = daily_cleaned[var].reindex(full_index)
                valid_count = series_full[eval_mask].notna().sum()
                pct = ((1- valid_count / total_days) * 100) if total_days > 0 else 0
                completeness_by_year[year][var] = {
                    "valid_days": int(valid_count),
                    "completeness_pct": pct,
                    "total_eval_days": int(total_days)
                }

    # Print summary
    print(f"{'Year':<8}", end="")
    for var in value_cols:
        print(f"{var:<12}", end="")
    print()
    print("-" * (8 + len(value_cols) * 12))

    for year in years_covered:
        print(f"{year:<8}", end="")
        for var in value_cols:
            if var in completeness_by_year[year]:
                completeness_pct = completeness_by_year[year][var]["completeness_pct"]
                missing_pct = 100.0 - completeness_pct
                print(f"{missing_pct:>10.1f}%  ", end="")
            else:
                print(f"{'N/A':>10}  ", end="")
        print()

    print()
    return completeness_by_year


def evaluate_station_quality(daily_cleaned, value_cols, miss_result_dict, summary_flags):
    """
    Evaluate overall station quality based on missing rates, flag rates, and large gaps.

    Parameters:
    -----------
    daily_cleaned : DataFrame
        Cleaned data
    value_cols : list
        Variables
    miss_result_dict : dict
        Missing check results
    summary_flags : dict
        Flagged value summaries

    Returns:
    --------
    variable_quality : dict
        Quality assessment per variable
    """
    print("=" * 80)
    print("STATION QUALITY EVALUATION SUMMARY (QC SCORING ENGINE)")
    print("=" * 80)
    print()

    # Thresholds
    THRESH = {
        "missing": {"caution": 20, "problematic": 30, "unusable": 60},
        "flag": {"caution": 20, "unreliable": 30},
        "gap_days": 365
    }

    PRIORITY = {"GOOD": 0, "CAUTION": 1, "UNRELIABLE": 2, "PROBLEMATIC": 3, "UNUSABLE": 4}

    quality_colors = {"GOOD": "✅", "CAUTION": "⚠️", "UNRELIABLE": "❌", "PROBLEMATIC": "⚠️⚠️", "UNUSABLE": "❌❌"}

    variable_quality = {}

    for var in value_cols:
        if var not in daily_cleaned.columns:
            continue

        series = daily_cleaned[var]
        missing_rate = miss_result_dict[var].get("missing_pct", 0)
        flag_rate = summary_flags[var]["flag_rate_percent"]

        # Missing rating
        if missing_rate >= THRESH["missing"]["unusable"]:
            missing_rating = "UNUSABLE"
        elif missing_rate >= THRESH["missing"]["problematic"]:
            missing_rating = "PROBLEMATIC"
        elif missing_rate >= THRESH["missing"]["caution"]:
            missing_rating = "CAUTION"
        else:
            missing_rating = "GOOD"

        # Flag rating
        if flag_rate >= THRESH["flag"]["unreliable"]:
            flag_rating = "UNRELIABLE"
        elif flag_rate >= THRESH["flag"]["caution"]:
            flag_rating = "CAUTION"
        else:
            flag_rating = "GOOD"

        # Large gap
        valid_data = series.dropna()
        has_large_gap = False
        if len(valid_data) >= 2:
            gaps = valid_data.index.to_series().diff().dt.days
            has_large_gap = (gaps > THRESH["gap_days"]).any()
        gap_rating = "CAUTION" if has_large_gap else "GOOD"

        ratings = [missing_rating, flag_rating, gap_rating]
        final_rating = max(ratings, key=lambda r: PRIORITY[r])

        issues = []
        if missing_rating != "GOOD":
            issues.append(f"Missing rate {missing_rate:.1f}%")
        if flag_rating != "GOOD":
            issues.append(f"Flag rate {flag_rate:.1f}%")
        if has_large_gap:
            issues.append("Large temporal gap > 1 year")

        variable_quality[var] = {
            "missing_rate": missing_rate,
            "flag_rate": flag_rate,
            "has_large_gap": has_large_gap,
            "missing_rating": missing_rating,
            "flag_rating": flag_rating,
            "gap_rating": gap_rating,
            "rating": final_rating,
            "issues": issues,
            "valid_records": series.notna().sum(),
            "total_records": len(series)
        }

    # Print per-variable results
    print("VARIABLE-BY-VARIABLE QUALITY ASSESSMENT")
    print("-" * 80)
    print()

    for var, q in variable_quality.items():
        icon = quality_colors[q["rating"]]
        print(f"{icon} {var.upper():<12} {q['rating']:<12}")
        print(f"   Missing rate: {q['missing_rate']:6.2f}%")
        print(f"   Flag rate:    {q['flag_rate']:6.2f}%")
        print(f"   Large gaps:   {'YES' if q['has_large_gap'] else 'NO'}")
        for issue in q["issues"]:
            print(f"   ⚠️ {issue}")
        print()

    # Temporal coverage
    print("TEMPORAL COVERAGE ASSESSMENT")
    print("-" * 80)
    print()

    years = sorted(daily_cleaned.index.year.unique())
    print(f"Period: {daily_cleaned.index.min().date()} → {daily_cleaned.index.max().date()}")
    print(f"Years: {years[0]}–{years[-1]} ({len(years)} years)")

    year_gaps = [(years[i], years[i+1]) for i in range(len(years)-1) if years[i+1] - years[i] > 1]
    if year_gaps:
        print(f"Status: ❌ NOT CONTINUOUS ({len(year_gaps)} gaps)")
    else:
        print("Status: ✅ CONTINUOUS")
    print()

    # Summary counts
    rating_counts = pd.Series([q["rating"] for q in variable_quality.values()]).value_counts().to_dict()
    print("SUMMARY:")
    for r in ["GOOD", "CAUTION", "UNRELIABLE", "PROBLEMATIC", "UNUSABLE"]:
        if r in rating_counts:
            print(f"  {quality_colors[r]} {r:<12}: {rating_counts[r]}")

    print()
    return variable_quality


def get_station_rating(variable_ratings):
    """
    Determine overall station quality rating from variable-level ratings.

    Parameters:
    -----------
    variable_ratings : list of str
        List like ["GOOD", "CAUTION", "UNRELIABLE", "PROBLEMATIC", ...]

    Returns:
    --------
    rating : str
    recommendation : str
    """
    n = len(variable_ratings)
    n_unusable = variable_ratings.count("UNUSABLE")
    n_problematic = variable_ratings.count("PROBLEMATIC")
    n_unreliable = variable_ratings.count("UNRELIABLE")
    n_caution = variable_ratings.count("CAUTION")

    if n_unusable > 0:
        return "❌❌ UNUSABLE STATION", "REJECT - Station has unusable variables"
    if n_problematic >= 0.5 * n:
        return "❌ POOR QUALITY", "REJECT or USE WITH CAUTION - High proportion of problematic variables"
    if (n_unreliable + n_problematic) >= 0.5 * n:
        return "⚠️⚠️ QUESTIONABLE QUALITY", "USE WITH CAUTION - High proportion of unreliable/problematic variables"
    if n_unreliable > 0 or n_problematic > 0:
        return "⚠️ MODERATE QUALITY", "USABLE with caution - Some variables require monitoring"
    if n_caution >= 2:
        return "⚠️ FAIR QUALITY", "USABLE - Most variables acceptable"
    return "✅ GOOD QUALITY", "USABLE - Data quality acceptable"