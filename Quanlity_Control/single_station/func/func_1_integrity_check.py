import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def detect_freq(index):
    dt = index.to_series().diff().dropna()
    return dt.mode()[0]



def check_missing_timestamps(df, value_col=None, freq=None, return_full=False):
    """
    Detect missing timestamps in a time series.

    Parameters
    ----------
    df : pd.DataFrame or pd.Series
        Must have DatetimeIndex
    freq : str or pd.Timedelta, optional
        If None → automatically detected
    return_full : bool
        If True, return reindexed dataframe

    Returns
    -------
    dict with:
        - freq
        - n_missing
        - missing_pct
        - missing_times
        - (optional) df_full
    """

    # --- ensure Series ---
    if value_col is None:
        series = df.iloc[:, 0]
    else:
        series = df[value_col]

    # --- detect frequency if not provided ---
    if freq is None:
        dt = series.index.to_series().diff().dropna()
        freq = dt.mode()[0]

    # --- build full timeline ---
    full_time = pd.date_range(
        start=series.index.min(),
        end=series.index.max(),
        freq=freq
    )

    # --- reindex ---
    df_full = series.reindex(full_time)

    # --- missing ---
    missing_mask = df_full.isna()
    missing_times = df_full.index[missing_mask]

    n_missing = missing_mask.sum()
    missing_pct = n_missing / len(full_time) * 100

    # --- output ---
    result = {
        "freq": freq,
        "n_missing": int(n_missing),
        "missing_pct": missing_pct,
        "missing_times": missing_times
    }

    if return_full:
        result["df_full"] = df_full

    return result
    
def qc_range_check(df, min_val=-20, max_val=20):
    """
    Quality control for threshold exceedance.

    Parameters
    ----------
    df : pd.DataFrame (time index, single column)
    min_val, max_val : float
        valid range

    Returns
    -------
    dict with:
        flag : 0/1 (out-of-range)
        deviation : distance from threshold
    """

    x = df.copy()

    # --- flag ---
    flag = ((x > max_val) | (x < min_val)).astype(int)

    # --- deviation (distance from nearest bound) ---
    deviation = x.copy().astype(float)

    deviation[x > max_val] = x[x > max_val] - max_val
    deviation[x < min_val] = min_val - x[x < min_val]
    deviation[(x >= min_val) & (x <= max_val)] = 0

    return {
        "flag": flag,
        "deviation": deviation
    }


### Visulization code
import matplotlib.pyplot as plt

def plot_timeseries_with_missing_multi(
    df,
    miss_result_dict,
    color_map,
    value_cols=None,
    figsize=(12, 2.5),
    alpha=0.6,
    lw=1.0,
    title="Time series with missing timestamps"
):

    if value_cols is None:
        value_cols = df.columns

    n = len(value_cols)

    fig, axes = plt.subplots(
        n, 1,
        figsize=(figsize[0], figsize[1] * n),
        sharex=True
    )

    if n == 1:
        axes = [axes]

    for ax, col in zip(axes, value_cols):

        series = df[col]
        color = color_map.get(col, "gray")

        # -------------------------
        # main series
        # -------------------------
        ax.plot(series.index, series, color=color, lw=lw, label=col)

        # -------------------------
        # missing info
        # -------------------------
        miss_info = miss_result_dict.get(col, None)

        if miss_info is not None:

            missing_times = miss_info["missing_times"]
            n_missing = miss_info.get("n_missing", len(missing_times))
            missing_pct = miss_info.get("missing_pct", 0)

            if len(missing_times) > 0:

                y_min = series.min()
                y_max = series.max()
                offset = (y_max - y_min) * 0.05 if y_max > y_min else 1

                ax.scatter(
                    missing_times,
                    [y_min - offset] * len(missing_times),
                    color= 'gray', #color,          # FIX: use variable color
                    marker="x",
                    alpha=alpha,
                    label="missing"
                )

            # -------------------------
            # annotation (NEW)
            # -------------------------
            text = f"{n_missing} missing ({missing_pct:.1f}%)"

            ax.text(
                0.01, 0.95, text,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle="round", alpha=0.2)
            )

        # styling
        ax.set_ylabel(col)
        ax.legend(loc="upper right")

    axes[0].set_title(title)

    plt.tight_layout()
    plt.show()