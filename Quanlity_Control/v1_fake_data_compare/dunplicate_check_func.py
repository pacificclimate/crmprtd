# Check for
# 1. Duplicate entire years: “All values in one year = another year”
# 2. Duplicate months within the same year: “One month = another month”
# 3. Same calendar month across years: “Jan 2000 = Jan 2001”
# 4. Identical value–streak checks: If the same value repeats for many consecutive days, it’s unusual and probably an error.


import numpy as np
import pandas as pd


def is_duplicate_series(s1, s2):
    """
    Compare two time series (ignore NaNs, align to shorter length)
    """
    n = min(len(s1), len(s2))
    
    a = s1[:n]
    b = s2[:n]

    # ignore NaNs
    mask = ~np.isnan(a) & ~np.isnan(b)

    if mask.sum() == 0:
        return False

    return np.allclose(a[mask], b[mask])


def detect_duplicate_years(df):
    """
    Detect years with identical time series
    """
    df = df.copy()
    df['year'] = df.index.year

    years = df['year'].unique()
    duplicates = []

    for i, y1 in enumerate(years):
        s1 = df[df['year'] == y1].iloc[:,0].values

        for y2 in years[i+1:]:
            s2 = df[df['year'] == y2].iloc[:,0].values

            if is_duplicate_series(s1, s2):
                duplicates.append((y1, y2))

    return duplicates


def detect_duplicate_months_within_year(df):
    df = df.copy()
    df['year'] = df.index.year
    df['month'] = df.index.month

    duplicates = []

    for year, group in df.groupby('year'):
        months = group['month'].unique()

        for i, m1 in enumerate(months):
            s1 = group[group['month'] == m1].iloc[:,0].values

            for m2 in months[i+1:]:
                s2 = group[group['month'] == m2].iloc[:,0].values

                if is_duplicate_series(s1, s2):
                    duplicates.append((year, m1, m2))

    return duplicates



def detect_duplicate_same_month_across_years(df):
    df = df.copy()
    df['year'] = df.index.year
    df['month'] = df.index.month

    duplicates = []

    for month, group in df.groupby('month'):
        years = group['year'].unique()

        for i, y1 in enumerate(years):
            s1 = group[group['year'] == y1].iloc[:,0].values

            for y2 in years[i+1:]:
                s2 = group[group['year'] == y2].iloc[:,0].values

                if is_duplicate_series(s1, s2):
                    duplicates.append((month, y1, y2))

    return duplicates



def identical_value_streak_check(df,column, threshold, skip_zeros=False):
    """
    Check for streaks of identical values in a time series.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a datetime index and columns of measurements
    column : str
        Column name to check
    threshold : int
        Minimum number of consecutive identical values to flag
    skip_zeros : bool
        Whether to ignore zeros in the streak (for PRCP/SNOW)

    Returns
    -------
    List of tuples:
        Each tuple contains (start_index, end_index, value) for flagged streaks
    """
    series = df[column].copy()
    flagged = []

    count = 1
    start_idx = 0

    for i in range(1, len(series)):
        prev_val = series.iloc[i-1]
        curr_val = series.iloc[i]

        # Skip zeros if needed
        if skip_zeros and (prev_val == 0 or curr_val == 0):
            if count >= threshold:
                flagged.append((start_idx, i-1, prev_val))
            count = 1
            start_idx = i
            continue

        # Treat missing as skipped
        if pd.isna(curr_val) or pd.isna(prev_val):
            continue

        if curr_val == prev_val:
            if count == 1:
                start_idx = i-1
            count += 1
        else:
            if count >= threshold:
                flagged.append((start_idx, i-1, prev_val))
            count = 1

    # Check last streak
    if count >= threshold:
        flagged.append((start_idx, len(series)-1, series.iloc[-1]))

    return flagged


        


def duplicate_check_temperature(df, column):
    """
    Run all duplicate checks for temperature data
    """

    result = {
        "duplicate_years": detect_duplicate_years(df),
        "duplicate_months_within_year": detect_duplicate_months_within_year(df),
        "duplicate_same_month_across_years": detect_duplicate_same_month_across_years(df),
        "identical_value_streaks": identical_value_streak_check(df, column, threshold=20)

    }

    return result

def print_duplicate_summary(result):
    print("\n===== DUPLICATE CHECK SUMMARY =====\n")

    has_issue = False

    # ---- Years ----
    if result["duplicate_years"]:
        has_issue = True
        print("📅 Duplicate Years:")
        for y1, y2 in result["duplicate_years"]:
            print(f"  - {int(y1)} == {int(y2)}")
    else:
        print("📅 Duplicate Years: None")

    # ---- Months within year ----
    if result["duplicate_months_within_year"]:
        has_issue = True
        print("\n📆 Duplicate Months (within year):")
        for y, m1, m2 in result["duplicate_months_within_year"]:
            print(f"  - Year {int(y)}: Month {int(m1)} == Month {int(m2)}")
    else:
        print("\n📆 Duplicate Months (within year): None")

    # ---- Months across years ----
    if result["duplicate_same_month_across_years"]:
        has_issue = True
        print("\n🌍 Duplicate Months (across years):")

        grouped = {}
        for m, y1, y2 in result["duplicate_same_month_across_years"]:
            key = (int(y1), int(y2))
            grouped.setdefault(key, []).append(int(m))

        for (y1, y2), months in grouped.items():
            if len(months) == 12:
                print(f"  - {y1} == {y2} (ALL months)")
            else:
                print(f"  - {y1} vs {y2}: months {months}")
    else:
        print("\n🌍 Duplicate Months (across years): None")
    # ---- Identical Value Streaks ----
    
    if result.get("identical_value_streaks"):
        streaks = result["identical_value_streaks"]
        if streaks:
            has_issue = True
            print("\n🔴 Identical Value Streaks:")
            for start_idx, end_idx, val in streaks:
                print(f"  - Streak from index {start_idx} to {end_idx}: value = {val}")
        else:
            print("\n🔴 Identical Value Streaks: None")
    else:
        print("\n🔴 Identical Value Streaks: None")
    # ---- FINAL STATUS ----
    print("\n---------------------------------")

    if not has_issue:
        print("✅ Duplicate check PASSED — no issues found")
    else:
        print("❌ Duplicate check FAILED — duplicates detected")

    print("=================================\n")

