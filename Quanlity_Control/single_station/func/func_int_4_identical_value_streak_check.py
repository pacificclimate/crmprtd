import pandas as pd
import numpy as np

def get_streak_threshold(value_col):
    """
    Return appropriate streak threshold for each variable.
    
    TMAX/TMIN: 20 or more
    SNOW: 90 or more (nonzero)
    SNWD: 90 or more (nonzero)
    PRECIP: 20 or more
    Default: 20
    """
    thresholds = {
        "tmax": 20,
        "tmin": 20,
        "snw_fall": 90,
        "snw_dpth": 90,
        "precip": 20,
        "ppt": 20,
    }
    return thresholds.get(value_col.lower(), 20)

def should_skip_zeros_for_streak(value_col):
    """
    Return True if zeros should be skipped in streak detection.
    SNOW and SNWD should skip zeros (we want nonzero streaks).
    """
    return value_col.lower() in ["snw_fall", "snw_dpth"]


def identical_value_streak_check(df, value_col, threshold, skip_zeros=False):
    """
    Return streaks of identical values using real datetime index.
    
    Parameters:
    -----------
    df : DataFrame
        Input data with datetime index
    value_col : str
        Column name to check
    threshold : int
        Minimum consecutive identical values to flag
    skip_zeros : bool
        If True, skip zero values in streak counting
    
    Returns:
    --------
    list of tuples
        (start_date, end_date, value) for each flagged streak
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
            count = 1
            start_idx = i
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
    
def identify_value_streaks(df, value_col):
    """
    Independent check for identical value streaks.
    Uses variable-specific thresholds.
    
    Returns dict with streak results and metadata.
    """
    threshold = get_streak_threshold(value_col)
    skip_zeros = should_skip_zeros_for_streak(value_col)
    
    streaks = identical_value_streak_check(
        df, value_col, threshold=threshold, skip_zeros=skip_zeros
    )
    
    return {
        "variable": value_col,
        "threshold": threshold,
        "skip_zeros": skip_zeros,
        "streaks": streaks
    }


def print_streak_summary(streak_result):
    """
    Print summary of identical value streak check.
    """
    print("\n===== IDENTICAL VALUE STREAK CHECK =====\n")

    variable = streak_result.get("variable")
    threshold = streak_result.get("threshold")
    skip_zeros = streak_result.get("skip_zeros")
    streaks = streak_result.get("streaks", [])

    print(f"Variable: {variable}")
    print(f"Threshold: {threshold} consecutive values")
    if skip_zeros:
        print(f"Skip zeros: YES (nonzero streaks only)")
    else:
        print(f"Skip zeros: NO")

    print()

    if streaks:
        print(f"🔴 Found {len(streaks)} identical value streak(s):")
        for start_idx, end_idx, val in streaks:
            duration = (end_idx - start_idx).days + 1
            print(f"  - {start_idx} → {end_idx} ({duration} days): value = {val}")
    else:
        print("✅ No suspicious identical value streaks detected")

    print("=========================================\n")


def streak_summary_for_report(streak_result):
    """
    Generate summary dict for streak check for reporting.
    """
    return {
        "variable": streak_result.get("variable"),
        "threshold": streak_result.get("threshold"),
        "skip_zeros": streak_result.get("skip_zeros"),
        "n_streaks": len(streak_result.get("streaks", [])),
        "total_flagged_days": sum(
            (end - start).days + 1 
            for start, end, _ in streak_result.get("streaks", [])
        )
    }