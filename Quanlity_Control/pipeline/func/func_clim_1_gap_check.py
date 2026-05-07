import numpy as np
import pandas as pd


def gap_check_two_tailed(df, value_col="temp", gap_threshold=10):
    """
    Gap check for two_tailed (two-tailed)

    Returns:
        flagged_indices: list of timestamps flagged as outliers
    """

    flagged = []

    # loop over months (1–12)
    for month in range(1, 13):

        # select all values for this calendar month
        sub = df[df.index.month == month][value_col].dropna()

        if len(sub) < 10:
            continue

        values = sub.values
        times = sub.index

        # --- sort ---
        sort_idx = np.argsort(values)
        sorted_vals = values[sort_idx]
        sorted_times = times[sort_idx]

        # --- median split ---
        median = np.median(sorted_vals)

        lower_mask = sorted_vals <= median
        upper_mask = sorted_vals >= median

        # --- check lower tail ---
        lower_vals = sorted_vals[lower_mask]
        lower_times = sorted_times[lower_mask]

        if len(lower_vals) > 1:
            diffs = np.diff(lower_vals)

            for i in range(len(diffs)):
                if diffs[i] > gap_threshold:
                    flagged.extend(lower_times[:i+1])  # everything below gap
                    break

        # --- check upper tail ---
        upper_vals = sorted_vals[upper_mask]
        upper_times = sorted_times[upper_mask]

        if len(upper_vals) > 1:
            diffs = np.diff(upper_vals)

            for i in range(len(diffs)):
                if diffs[i] > gap_threshold:
                    flagged.extend(upper_times[i+1:])  # everything above gap
                    break

    # ✅ convert to boolean Series
    flag_series = pd.Series(False, index=df.index, name=value_col)
    flag_series.loc[list(set(flagged))] = True

    return {
        "flag": flag_series
    }

def gap_check_one_tailed(df, value_col="precip", gap_threshold=300):

    flagged = []

    for month in range(1, 13):

        sub = df[df.index.month == month][value_col].dropna()
        sub = sub[sub > 0]

        if len(sub) < 10:
            continue

        values = sub.values
        times = sub.index

        sort_idx = np.argsort(values)
        sorted_vals = values[sort_idx]
        sorted_times = times[sort_idx]

        diffs = np.diff(sorted_vals)

        for i in range(len(diffs)):
            if diffs[i] > gap_threshold:
                flagged.extend(sorted_times[i+1:])
                break

    flag_series = pd.Series(False, index=df.index, name=value_col)
    flag_series.loc[list(set(flagged))] = True

    return {
        "flag": flag_series
    }