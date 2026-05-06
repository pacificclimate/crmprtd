"""
Generate flat summary tables from QC results for reporting and analysis.
"""
import pandas as pd
import numpy as np


def create_cleaned_dataset_with_flags(
    station_id,
    daily_cleaned,
    naught_all,
    range_result_dict,
    dup_result_dict,
    ind_result_dict,
    gap_result_dict,
    clim_flag_df,
    inttemp_tas_result,
    inttemp_snow_tmin_result,
    inttemp_snow_fall_dpth_result,
    inttemp_snow_precip_result,
    value_cols=None
):
    """
    Combine cleaned data with all QC flags into a single flat table.
    
    Returns:
        pd.DataFrame with columns: date, (cleaned values), (all flag columns)
    """
    if value_cols is None:
        value_cols = ["temp", "tmin", "tmax", "precip", "snw_fall", "snw_dpth"]
    
    result = daily_cleaned.copy()
    result['date'] = result.index

    result['station_id'] = station_id
    result.insert(0, 'station_id', result.pop('station_id'))
    result.insert(1, 'date', result.pop('date'))


    # Naught flags
    for col in value_cols:
        if col in naught_all.columns:
            flag_col = f"flag_naught_{col}"
            result[flag_col] = naught_all[col].astype(int)

    
    
    # Duplicate/flatline flags for all variables
    for col in value_cols:
        if col in dup_result_dict:
            var_dup_results = dup_result_dict[col]
            
            # Handle duplicate years - create flag column from detected duplicates
            if 'duplicate_years' in var_dup_results and var_dup_results['duplicate_years'] is not None:
                dup_years_list = var_dup_results['duplicate_years']
                result[f'flag_dup_years_{col}'] = result.index.year.isin([y for pair in dup_years_list for y in pair]).astype(int)
            elif col == 'snw_dpth':
                # SNWD skips duplicate years check
                result[f'flag_dup_years_{col}'] = 0
            
            # Handle duplicate months within year
            if col != 'snw_dpth' and var_dup_results.get('duplicate_months_within_year') is not None:
                dup_months_within = var_dup_results['duplicate_months_within_year']

                monthly_flags = pd.Series(False, index=result.index)

                for year, m1, m2 in dup_months_within:
                    mask1 = (result.index.year == year) & (result.index.month == m1)
                    mask2 = (result.index.year == year) & (result.index.month == m2)
                    monthly_flags |= mask1 | mask2

                result[f'flag_dup_months_within_{col}'] = monthly_flags.astype(int)


            # Handle duplicate months across years
            if col != 'snw_dpth' and var_dup_results.get('duplicate_same_month_across_years') is not None:
                dup_months_across = var_dup_results['duplicate_same_month_across_years']

                monthly_flags = pd.Series(False, index=result.index)

                for month, y1, y2 in dup_months_across:
                    mask1 = (result.index.year == y1) & (result.index.month == month)
                    mask2 = (result.index.year == y2) & (result.index.month == month)
                    monthly_flags |= mask1 | mask2

                result[f'flag_dup_months_across_{col}'] = monthly_flags.astype(int)
            
            # Special case for tmin/tmax flatline checks
            if col in ['tmin', 'tmax'] and 'tmin_tmax_equal' in var_dup_results:
                tmin_tmax_flags = var_dup_results['tmin_tmax_equal']
                if 'tmin_tmax_equal' in tmin_tmax_flags.columns:
                    result['flag_dup_month_tmin_tmax_equal'] = tmin_tmax_flags['tmin_tmax_equal'].astype(int)
    

    # Range flags
    for col in value_cols:
        if col in range_result_dict:
            flag_col = f"flag_range_{col}"
            result[flag_col] = range_result_dict[col]['flag'].astype(int)


    # Identical value streak flags
    for col in value_cols:
        if col in ind_result_dict:
            streak_mask = pd.Series(False, index=result.index)
            streaks = ind_result_dict.get(col, {}).get("streaks", [])
            for start, end, _ in streaks:
                streak_mask |= (result.index >= pd.to_datetime(start)) & (
                    result.index <= pd.to_datetime(end))
            result[f"flag_streak_{col}"] = streak_mask.astype(int)
    
    # Gap flags
    for col in gap_result_dict:
        if "flag" in gap_result_dict[col]:
            result[f"flag_gap_{col}"] = gap_result_dict[col]["flag"].astype(int)
    
    # Climatological outlier flags
    if clim_flag_df is not None:
        for col in clim_flag_df.columns:
            result[f"flag_clim_{col}"] = clim_flag_df[col].astype(int)
    
    # Internal temporal consistency flags
    # flag_inttemp_tas_check
    wanted_cols = ["flag_basic", "flag_spike", "flag_lag"]
    cols = [c for c in wanted_cols if c in inttemp_tas_result.columns]

    result[[f"flag_inttemp_tas_{c}" for c in cols]] = (
        inttemp_tas_result[cols].fillna(0).astype(int)
    )
    
    # flag_inttemp_snow_tmin_check
    wanted_cols = ["flag_snow_warm", "flag_snwd_warm"]
    cols = [c for c in wanted_cols if c in inttemp_snow_tmin_result.columns]

    result[[f"flag_inttemp_snow_tmin_{c}" for c in cols]] = (
        inttemp_snow_tmin_result[cols].fillna(0).astype(int)
    )

    # flag_inttemp_snow_fall_dpth_check
    wanted_cols = ["flag_snow_snwd", "flag_snwd_prev"]
    cols = [c for c in wanted_cols if c in inttemp_snow_fall_dpth_result.columns]

    result[[f"flag_inttemp_snow_fall_dpth_{c}" for c in cols]] = (
        inttemp_snow_fall_dpth_result[cols].fillna(0).astype(int)
    )

    # flag_inttemp_snow_precip_check
    wanted_cols = ["flag_snow", "flag_snwd", "flag_prcp", "flag_snwd_prev"]
    cols = [c for c in wanted_cols if c in inttemp_snow_precip_result.columns]

    result[[f"flag_inttemp_snow_precip_{c}" for c in cols]] = (
        inttemp_snow_precip_result[cols].fillna(0).astype(int)
    )

    # Missing value flag
    for col in value_cols:
        result[f"is_missing_{col}"] = result[col].isna().astype(int)
    
    # print(result.reset_index(drop=True))
    
    # flag_cols = [c for c in result.columns if c.startswith("flag_")]

    # sum_row = result[flag_cols].sum()
    # sum_row.name = "sum"

    # result = pd.concat([result, sum_row.to_frame().T])

    return result.reset_index(drop=True)


def decode_itc_column(col_name):
    """
    Return list of (variable, flag_type) tuples for a given column.
    Some columns map to multiple variables.
    """

    # --- TAS group ---
    if col_name.startswith('flag_inttemp_tas_'):
        suffix = col_name.replace('flag_inttemp_tas_flag_', '')
        flag_type = f'inttemp_tas_{suffix}'

        return [(v, flag_type) for v in ['temp', 'tmax', 'tmin']]

    # --- snow_tmin group ---
    if col_name == 'flag_inttemp_snow_tmin_flag_snow_warm':
        return [('snw_fall', 'inttemp_snow_warm')]

    if col_name == 'flag_inttemp_snow_tmin_flag_snwd_warm':
        return [('snw_dpth', 'inttemp_snow_warm')]

    # --- snow_fall_dpth group ---
    if col_name == 'flag_inttemp_snow_fall_dpth_flag_snow_snwd':
        return [
            ('snw_fall', 'inttemp_snw_fall_depth'),
            ('snw_dpth', 'inttemp_snw_fall_depth')
        ]

    if col_name == 'flag_inttemp_snow_fall_dpth_flag_snwd_prev':
        return [('snwd_prev', 'inttemp_snw_fall_depth')]

    # --- snow_precip group (similar pattern, adjust if needed) ---
    if col_name == 'flag_inttemp_snow_precip_flag_snow':
        return [('snw_fall', 'inttemp_snow_precip')]

    if col_name == 'flag_inttemp_snow_precip_flag_snwd':
        return [('snw_dpth', 'inttemp_snow_precip')]

    if col_name == 'flag_inttemp_snow_precip_flag_prcp':
        return [('precip', 'inttemp_snow_precip')]

    if col_name == 'flag_inttemp_snow_precip_flag_snwd_prev':
        return [('snwd_prev', 'inttemp_snow_precip')]


    return []


def create_flag_summary(cleaned_with_flags, station_id, value_cols=None, miss_result_dict=None):
    """
    Summary of all flags by variable and flag type.
    
    Parameters:
    -----------
    cleaned_with_flags : DataFrame
        Cleaned data with all flags
    station_id : int
        Station ID
    value_cols : list
        Variable columns
    miss_result_dict : dict
        Missing check results (from func_int_5_missing_check) for accurate missing percentages
    
    Returns:
        pd.DataFrame with columns: station_id, variable, flag_type, count, percentage
    """
    if value_cols is None:
        value_cols = ["temp", "tmin", "tmax", "precip", "snw_fall", "snw_dpth"]
    
    records = []
    total_rows = len(cleaned_with_flags)
    
    # Naught flags
    for col in value_cols:
        flag_col = f"flag_naught_{col}"
        if flag_col in cleaned_with_flags.columns:
            count = int(cleaned_with_flags[flag_col].fillna(0).sum())
            pct = (count / total_rows * 100) if total_rows > 0 else 0
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'naught',
                'count': count,
                'percentage': round(pct, 2)
            })

    # Range flags - use miss_result_dict
    for col in value_cols:
        flag_col = f"flag_range_{col}"
        if flag_col in cleaned_with_flags.columns:
            count = int(cleaned_with_flags[flag_col].fillna(0).sum())
            pct = (count / total_rows * 100) if total_rows > 0 else 0
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'range',
                'count': count,
                'percentage': round(pct, 2)
            })

    # Duplicate flags for all variables
    for col in value_cols:
        # Duplicate years
        flag_col = f'flag_dup_years_{col}'
        if flag_col in cleaned_with_flags.columns:
            count = int(cleaned_with_flags[flag_col].fillna(0).sum())
            pct = (count / total_rows * 100) if total_rows > 0 else 0
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'duplicate_years',
                'count': count,
                'percentage': round(pct, 2)
            })
        
        # Duplicate months within year
        flag_col = f'flag_dup_months_within_{col}'
        if flag_col in cleaned_with_flags.columns:
            count = int(cleaned_with_flags[flag_col].fillna(0).sum())
            pct = (count / total_rows * 100) if total_rows > 0 else 0
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'duplicate_months_within_year',
                'count': count,
                'percentage': round(pct, 2)
            })
        
        # Duplicate months across years
        flag_col = f'flag_dup_months_across_{col}'
        if flag_col in cleaned_with_flags.columns:
            count = int(cleaned_with_flags[flag_col].fillna(0).sum())
            pct = (count / total_rows * 100) if total_rows > 0 else 0
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'duplicate_months_across_years',
                'count': count,
                'percentage': round(pct, 2)
            })
    
    # Special tmin/tmax flatline flags
    if 'flag_dup_month_tmin_tmax_equal' in cleaned_with_flags.columns:
        count = int(cleaned_with_flags['flag_dup_month_tmin_tmax_equal'].fillna(0).sum())
        pct = (count / total_rows * 100) if total_rows > 0 else 0
        records.append({
            'station_id': station_id,
            'variable': 'tmin_tmax',
            'flag_type': 'tmax_tmin_month_equal',
            'count': count,
            'percentage': round(pct, 2)
        })
    

    # Missing flags - use miss_result_dict
    for col in value_cols:
        flag_col = f"is_missing_{col}"
        if flag_col in cleaned_with_flags.columns:
            count = miss_result_dict[col].get("n_missing")
            # Use miss_result_dict percentage if available (more accurate)
            pct = miss_result_dict[col].get("missing_pct")
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'missing',
                'count': count,
                'percentage': round(pct, 2)
            })

    # Streak flags
    for col in value_cols:
        flag_col = f"flag_streak_{col}"
        if flag_col in cleaned_with_flags.columns:
            count = int(cleaned_with_flags[flag_col].fillna(0).sum())
            pct = (count / total_rows * 100) if total_rows > 0 else 0
            # if count > 0:
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'streak',
                'count': count,
                'percentage': round(pct, 2)
            })


    # Gap flags
    for col in value_cols:
        flag_col = f"flag_gap_{col}"
        if flag_col in cleaned_with_flags.columns:
            count = int(cleaned_with_flags[flag_col].fillna(0).sum())
            pct = (count / total_rows * 100) if total_rows > 0 else 0
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'gap',
                'count': count,
                'percentage': round(pct, 2)
            })
    
    # Climatological flags
    for col in value_cols:
        flag_col = f"flag_clim_{col}"
        if flag_col in cleaned_with_flags.columns:
            count = int(cleaned_with_flags[flag_col].fillna(0).sum())
            pct = (count / total_rows * 100) if total_rows > 0 else 0
            records.append({
                'station_id': station_id,
                'variable': col,
                'flag_type': 'climatological',
                'count': count,
                'percentage': round(pct, 2)
            })
    

    # Internal temporal consistency flags
    itc_cols = cleaned_with_flags.filter(like='flag_inttemp_').columns

    for col_name in itc_cols:

        count = cleaned_with_flags[col_name].sum()
        pct = (count / total_rows * 100) if total_rows > 0 else 0

        mappings = decode_itc_column(col_name)

        for var, flag_type in mappings:
            records.append({
                'station_id': station_id,
                'variable': var,
                'flag_type': flag_type,
                'count': int(count),
                'percentage': round(pct, 2)
            })
    
    return pd.DataFrame(records)

def summarize_variable_flag_rate(flag_summary_df):
    """
    Compute flag rate per variable using selected flag types only.
    """
    value_cols = ["temp", "tmin", "tmax", "precip", "snw_fall", "snw_dpth"]
    # --- keep only relevant flag types ---
    df = flag_summary_df[
        (flag_summary_df["flag_type"] == "gap") |
        (flag_summary_df["flag_type"] == "climatological") |
        (flag_summary_df["flag_type"].str.startswith("inttemp_"))
    ]

    # --- aggregate ---
    summary = (
        df.groupby(["station_id", "variable"], as_index=False)
          .agg(
              total_flag_count=("count", "sum"),
              # percentages already relative to total_rows → can sum approximately
              total_flag_pct=("percentage", "sum")
        )
    )
    return summary

def create_station_evaluation_summary(
    station_id,
    analysis_start_date,
    analysis_end_date,
    years_covered,
    completeness_by_year,
    variable_quality,
    station_rating,
    recommendation,
    value_cols=None
):
    """
    Station and variable-level evaluation summary.
    
    Returns:
        pd.DataFrame with one row per variable, including:
        - station_id, analysis_period_start, analysis_period_end
        - years_covered, large_gaps, variable, missing_rate, flag_rate, rating
    """
    if value_cols is None:
        value_cols = ["temp", "tmin", "tmax", "precip", "snw_fall", "snw_dpth"]
    
    records = []
    
    # Extract year range from completeness_by_year or use years_covered
    if isinstance(years_covered, str):
        year_range = years_covered
    else:
        year_range = f"{years_covered[0]}–{years_covered[-1]}" if years_covered else "N/A"
    
    for var in value_cols:
        var_info = variable_quality.get(var, {})
        
        has_large_gap = "YES" if var_info.get('has_large_gap', False) else "NO"
        
        records.append({
            'station_id': station_id,
            'variable': var,
            'analysis_period_start': analysis_start_date,
            'analysis_period_end': analysis_end_date,
            'years_covered': year_range,
            'total_years': len(years_covered) if isinstance(years_covered, (list, tuple)) else 1,
            'large_gaps': has_large_gap,
            'missing_rate_pct': round(var_info.get('missing_rate', 0), 2),
            'flag_rate_pct': round(var_info.get('flag_rate', 0), 2),
            'rating': var_info.get('rating', 'UNKNOWN'),
        })
    
    # Add overall station summary as an aggregate row
    records.append({
        'station_id': station_id,
        'variable': '*** STATION OVERALL ***',
        'analysis_period_start': analysis_start_date,
        'analysis_period_end': analysis_end_date,
        'years_covered': year_range,
        'total_years': len(years_covered) if isinstance(years_covered, (list, tuple)) else 1,
        'large_gaps': 'N/A',
        'missing_rate_pct': None,
        'flag_rate_pct': None,
        'rating': station_rating,
    })
    
    return pd.DataFrame(records)
