import pandas as pd
import numpy as np


import pandas as pd
import numpy as np


def get_snow_seasons(df, col="snw_fall", threshold=0.1, max_gap_days=90):
    """
    Detect continuous snow seasons with gap tolerance.

    A new season starts only if:
    - snow resumes after a gap > max_gap_days
    """

    s = pd.to_numeric(df[col], errors="coerce")

    snow = (s > threshold).astype(int)

    idx = df.index

    seasons = []

    in_season = False
    start = None
    last_snow_day = None

    for i in range(len(snow)):

        if snow.iloc[i] == 1:

            if not in_season:
                # start new season
                start = idx[i]
                in_season = True

            last_snow_day = idx[i]

        else:

            if in_season and last_snow_day is not None:

                gap = (idx[i] - last_snow_day).days

                # only end season if gap is large enough
                if gap > max_gap_days:
                    seasons.append((start, last_snow_day))
                    in_season = False
                    start = None
                    last_snow_day = None

    # close last season
    if in_season and start is not None:
        seasons.append((start, last_snow_day))

    return seasons


# --------------------------------------------------
# 2. Main function (UPDATED)
# --------------------------------------------------
def check_missing_timestamps(df, value_col=None, freq=None, return_full=False):
    """
    Detect missing timestamps in a time series.

    Snow variables use event-based continuous seasonal windows:
    - snw_fall: snowfall-defined continuous seasons
    - snw_dpth: snowfall-defined continuous seasons (consistent denominator)
    """

    # --- ensure Series ---
    if isinstance(df, pd.Series):
        series = df
        col_name = series.name

    else:
        series = df[value_col] if value_col else df.iloc[:, 0]
        col_name = value_col

        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]

    series = pd.to_numeric(series, errors="coerce").squeeze()

    # --- frequency detection ---
    if freq is None:
        dt = series.index.to_series().diff().dropna()
        freq = dt.mode()[0]

    # --- full timeline ---
    full_time = pd.date_range(
        start=series.index.min(),
        end=series.index.max(),
        freq=freq
    )

    df_full = series.reindex(full_time)

    missing_mask = df_full.isna()
    missing_times = df_full.index[missing_mask]

    n_missing = missing_mask.sum()

    total_eval = len(full_time)
    missing_pct = n_missing / total_eval * 100

    # --------------------------------------------------
    # SNOW SPECIAL CASE (EVENT-BASED SEASON)
    # --------------------------------------------------
    if col_name in ["snw_fall", "snw_dpth"]:

        # snow season defined from snowfall activity
        season_bounds = get_snow_seasons(df, "snw_fall")
        print(season_bounds)

        missing_eval = 0
        total_eval_season = 0

        # IMPORTANT: collect seasonal missing times
        seasonal_missing_times = []

        for start, end in season_bounds:

            mask = (full_time >= start) & (full_time <= end)

            total_eval_season += mask.sum()

            missing_eval += missing_mask[mask].sum()

            seasonal_missing_times.append(df_full.index[mask & missing_mask])

        # flatten list of timestamps
        missing_times = pd.Index([]).append(
            pd.Index(np.concatenate(seasonal_missing_times))
            if len(seasonal_missing_times) > 0 else pd.Index([])
        )

        missing_pct = (
            (missing_eval / total_eval_season * 100)
            if total_eval_season > 0 else np.nan
        )

        total_eval = total_eval_season
        n_missing = missing_eval

    # --------------------------------------------------
    # OUTPUT
    # --------------------------------------------------
    result = {
        "freq": freq,
        "n_missing": int(n_missing),
        "missing_pct": missing_pct,
        "missing_times": missing_times,
        "n_total_eval": int(total_eval)
    }

    if return_full:
        result["df_full"] = df_full

    return result