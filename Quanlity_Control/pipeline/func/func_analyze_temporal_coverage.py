import pandas as pd
import numpy as np


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
    # print("=" * 70)
    # print("TEMPORAL COVERAGE ANALYSIS")
    # print("=" * 70)
    # print()

    # 1. Overall dataset coverage
    start_date = daily_cleaned.index.min()
    end_date = daily_cleaned.index.max()
    total_span = (end_date - start_date).days + 1

    # print(f"Dataset period: {start_date.date()} to {end_date.date()}")
    # print(f"Total span: {total_span} days (~{total_span/365.25:.2f} years)")
    # print()

    # 2. Years covered
    years_covered = daily_cleaned.index.year.unique()
    years_covered = sorted(years_covered)
    n_years = len(years_covered)

    # print(f"Years covered: {years_covered[0]} to {years_covered[-1]} ({n_years} years)")
    # print()

    # 3. Continuous years check
    year_gaps = []
    for i in range(len(years_covered) - 1):
        if years_covered[i + 1] - years_covered[i] > 1:
            year_gaps.append((years_covered[i], years_covered[i + 1]))

    # if year_gaps:
    #     print("❌ Data is NOT continuous (yearly gaps detected):")
    #     for y1, y2 in year_gaps:
    #         print(f"  - Gap between {y1} and {y2} ({y2 - y1} years missing)")
    # else:
    #     print("✅ Continuous years: All years from", years_covered[0], "to", years_covered[-1], "are covered")
    # print()

    # # 4. Large gaps (> 1 year) analysis by variable
    # print("Large gaps check (> 1 year = 365 days):")
    # print("-" * 70)

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

        # if gaps:
        #     print(f"{var}: ⚠️ {len(gaps)} large gap(s) detected")
        #     for gap in gaps:
        #         print(f"  - {gap['start_date'].date()} → {gap['end_date'].date()}: {gap['gap_days']} days ({gap['gap_years']:.1f} years)")
        # else:
        #     print(f"{var}: ✅ No large gaps (all gaps < 1 year)")

    # print()

    # 5. Data completeness by year and variable
    # print("=" * 70)
    # print("DATA COMPLETENESS BY YEAR AND VARIABLE")
    # print("=" * 70)
    # print()

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
    # print(f"{'Year':<8}", end="")
    # for var in value_cols:
    #     print(f"{var:<12}", end="")
    # print()
    # print("-" * (8 + len(value_cols) * 12))

    # for year in years_covered:
    #     print(f"{year:<8}", end="")
    #     for var in value_cols:
    #         if var in completeness_by_year[year]:
    #             completeness_pct = completeness_by_year[year][var]["completeness_pct"]
    #             missing_pct = 100.0 - completeness_pct
    #             print(f"{missing_pct:>10.1f}%  ", end="")
    #         else:
    #             print(f"{'N/A':>10}  ", end="")
    #     print()

    # print()
    return completeness_by_year