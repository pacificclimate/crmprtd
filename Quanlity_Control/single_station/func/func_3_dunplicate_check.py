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



def identical_value_streak_check(df, value_col, threshold, skip_zeros=False):
    """
    Return streaks of identical values using real datetime index.
    """

    series = df[value_col]
    flagged = []

    count = 1
    start_idx = 0

    for i in range(1, len(series)):
        prev_val = series.iloc[i - 1]
        curr_val = series.iloc[i]

        # Skip zeros if needed
        if skip_zeros and (prev_val == 0 or curr_val == 0):
            if count >= threshold:
                flagged.append((
                    df.index[start_idx],
                    df.index[i - 1],
                    prev_val
                ))
            count = 1
            start_idx = i
            continue

        # Skip missing
        if pd.isna(curr_val) or pd.isna(prev_val):
            continue

        if curr_val == prev_val:
            if count == 1:
                start_idx = i - 1
            count += 1
        else:
            if count >= threshold:
                flagged.append((
                    df.index[start_idx],
                    df.index[i - 1],
                    prev_val
                ))
            count = 1

    # last streak
    if count >= threshold:
        flagged.append((
            df.index[start_idx],
            df.index[len(series) - 1],
            series.iloc[-1]
        ))

    return flagged


        

def qc_tmax_tmin_flatline(df,
                          tmax_col="tmax",
                          tmin_col="tmin",
                          threshold_days=10):

    df = df.copy()

    # ensure datetime index
    df = df.sort_index()

    # monthly grouping
    month_group = df.index.to_period("M")

    # daily condition: TMAX == TMIN (ignore NaN)
    equal_flag = (df[tmax_col] == df[tmin_col]) & df[tmax_col].notna() & df[tmin_col].notna()

    # count per month
    monthly_count = equal_flag.groupby(month_group).sum()

    # months to flag
    bad_months = monthly_count >= threshold_days

    # map back to daily level
    flag_month = month_group.isin(bad_months[bad_months].index)

    flags = pd.DataFrame(index=df.index)

    flags["flag_tmax_tmin_equal"] = equal_flag.astype(bool)
    flags["flag_month_flatline"] = flag_month.astype(bool)

    return flags


def duplicate_check_temperature(df, value_col):
    """
    Run duplicate checks depending on variable type.
    """

    result = {}

    # -------------------------------------------------
    # always-run checks (except SNWD special case below)
    # -------------------------------------------------
    if value_col != "snw_dpth":
        result["duplicate_years"] = detect_duplicate_years(df)
        result["duplicate_months_within_year"] = detect_duplicate_months_within_year(df)
        result["duplicate_same_month_across_years"] = detect_duplicate_same_month_across_years(df)

        result["identical_value_streaks"] = identical_value_streak_check(
            df, value_col, threshold=20
        )
    else:
        # SNWD skips these checks
        result["duplicate_years"] = None
        result["duplicate_months_within_year"] = None
        result["duplicate_same_month_across_years"] = None
        result["identical_value_streaks"] = None

    # -------------------------------------------------
    # tmin / tmax specific logic
    # -------------------------------------------------
    if value_col in ["tmin", "tmax"]:
        result["tmin_tmax_equal"] = qc_tmax_tmin_flatline(df)
    else:
        result["tmin_tmax_equal"] = None

    return result

def print_duplicate_summary(result, value_col):
    print("\n===== DUPLICATE CHECK SUMMARY =====\n")

    has_issue = False

    # -------------------------------------------------
    # SNWD: skip heavy checks (by column name only)
    # -------------------------------------------------
    is_snwd = "snw" in value_col and "dpth" in value_col
    is_temp = value_col in ["tmin", "tmax"]

    if is_snwd:
        print("❄️ SNOW DEPTH VARIABLE")
        print("   - duplicate_months_within_year: skipped")
        print("   - duplicate_same_month_across_years: skipped")
        print("   - identical_value_streaks: skipped\n")

    # ---- Years ----
    if result.get("duplicate_years"):
        has_issue = True
        print("📅 Duplicate Years:")
        for y1, y2 in result["duplicate_years"]:
            print(f"  - {int(y1)} == {int(y2)}")
    else:
        print("📅 Duplicate Years: None")

    # ---- Months within year ----
    if not is_snwd:
        if result.get("duplicate_months_within_year"):
            has_issue = True
            print("\n📆 Duplicate Months (within year):")
            for y, m1, m2 in result["duplicate_months_within_year"]:
                print(f"  - Year {int(y)}: Month {int(m1)} == Month {int(m2)}")
        else:
            print("\n📆 Duplicate Months (within year): None")
    else:
        print("\n📆 Duplicate Months (within year): SKIPPED")

    # ---- Months across years ----
    if not is_snwd:
        if result.get("duplicate_same_month_across_years"):
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
    else:
        print("\n🌍 Duplicate Months (across years): SKIPPED")

    # ---- Identical Value Streaks ----
    streaks = result.get("identical_value_streaks", None)

    if not is_snwd:
        if streaks:
            has_issue = True
            print("\n🔴 Identical Value Streaks:")
            for start_idx, end_idx, val in streaks:
                print(f"  - {start_idx} → {end_idx}: value = {val}")
        else:
            print("\n🔴 Identical Value Streaks: None")
    else:
        print("\n🔴 Identical Value Streaks: SKIPPED")

    # ---- TMAX / TMIN flatline (ONLY by name) ----
    if value_col in ["tmin", "tmax"]:
        tmax_tmin = result.get("tmin_tmax_equal", None)

        if tmax_tmin is not None:
            flag_flatline = tmax_tmin.get("flag_month_flatline", None)

            if flag_flatline is not None and flag_flatline.any():
                has_issue = True
                print("\n🌡️ TMAX–TMIN Flatline Months:")
                flagged_days = flag_flatline[flag_flatline == 1].index
                print(f"  - Flatline days: {len(flagged_days)}")
                print(f"  - Example dates: list(flagged_days[:5])")
            else:
                print("\n🌡️ TMAX–TMIN Flatline Months: None")

    # ---- FINAL STATUS ----
    print("\n---------------------------------")

    if not has_issue:
        print("✅ Duplicate check PASSED — no issues found")
    else:
        print("❌ Duplicate check FAILED — duplicates detected")

    print("=================================\n")


def duplicate_summary_for_ppt(result, value_col):

    is_snwd = "snw" in value_col and "dpth" in value_col
    is_temp = value_col in ["tmin", "tmax"]

    summary = {
        "variable": value_col,
        "is_snwd": is_snwd,

        "n_duplicate_years": len(result.get("duplicate_years", [])) if result.get("duplicate_years") else 0,

        "n_duplicate_months_within_year": 0 if is_snwd else
            (len(result.get("duplicate_months_within_year", [])) if result.get("duplicate_months_within_year") else 0),

        "n_duplicate_months_across_years": 0 if is_snwd else
            (len(result.get("duplicate_same_month_across_years", [])) if result.get("duplicate_same_month_across_years") else 0),

        "n_streaks": 0 if is_snwd else
            (len(result.get("identical_value_streaks", [])) if result.get("identical_value_streaks") else 0),

        # default: always 0 unless tmin/tmax
        "tmax_tmin_flatline_days": 0
    }

    # -------------------------------------------------
    # ONLY tmin/tmax get flatline check
    # -------------------------------------------------
    if is_temp:
        tmax_tmin = result.get("tmin_tmax_equal")

        if tmax_tmin is not None:
            flat = tmax_tmin.get("flag_month_flatline")

            if flat is not None:
                summary["tmax_tmin_flatline_days"] = int(flat.sum())

    return summary