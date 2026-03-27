import pandas as pd
import numpy as np

def create_integrity_test_temperature_df():
    """
    Create synthetic temperature data with intentional duplicates, missing values,
    and identical-value streaks for QC testing.
    """
    # --- Create daily time index ---
    time = pd.date_range("2010-01-01", "2015-12-31", freq="D")

    np.random.seed(42)
    temp = (
        10
        + 20 * np.sin(2 * np.pi * time.dayofyear / 365)
        + np.random.normal(0, 1, len(time))
    )

    df = pd.DataFrame({"temp": temp}, index=time)

    # --- 1. Duplicate year (avoid leap year issue) ---
    df.loc["2013"] = df.loc["2011"].values

    # --- 2. Duplicate months (same year) ---
    jan = df.loc["2014-01"].values
    feb_idx = df.loc["2014-02"].index
    df.loc[feb_idx, "temp"] = jan[:len(feb_idx)].flatten()

    # --- 3. Same month across years ---
    mar_2010 = df.loc["2010-03"].values
    mar_2015_idx = df.loc["2015-03"].index
    df.loc[mar_2015_idx, "temp"] = mar_2010[:len(mar_2015_idx)].flatten()

    # --- 4. Introduce missing values (NaN) ---
    nan_idx = np.random.choice(len(df), size=30, replace=False)
    df.iloc[nan_idx, 0] = np.nan

    # --- 5. Introduce identical value streaks (21+ days) ---
    # Pick a start date
    streak_start = pd.Timestamp("2012-07-01")
    streak_length = 25  # >20 days
    df.loc[streak_start : streak_start + pd.Timedelta(days=streak_length - 1), "temp"] = 15.0

    return df

# Example usage
# df_test = create_test_temperature_df()
# print(df_test.head(40))

import numpy as np
import pandas as pd

def generate_synthetic_weather_data(start="2015-01-01", end="2020-12-31", seed=42):
    """
    Generate synthetic daily temperature and precipitation data with
    issues distributed across multiple years.
    """
    np.random.seed(seed)
    time = pd.date_range(start, end, freq="D")
    n = len(time)

    # --- Base signals ---
    temp = 10 + 10 * np.sin(2 * np.pi * time.dayofyear / 365) + np.random.normal(0, 1, n)
    precip = np.random.gamma(shape=1.0, scale=1.5, size=n)

    df = pd.DataFrame({"temp": temp, "precip": precip}, index=time)

    # --- Loop over each year ---
    for year in df.index.year.unique():

        df_year = df.loc[str(year)]
        idx = df_year.index

        # --- 1. Outliers (random positions per year) ---
        outlier_days = np.random.choice(len(idx), size=3, replace=False)
        df.loc[idx[outlier_days], "temp"] += np.random.choice([20, -15, 25], size=3)
        df.loc[idx[outlier_days], "precip"] += np.random.choice([30, 50, 40], size=3)

        # --- 2. Missing values ---
        miss_days = np.random.choice(len(idx), size=3, replace=False)
        df.loc[idx[miss_days], "temp"] = np.nan
        df.loc[idx[miss_days], "precip"] = np.nan

        # --- 3. Identical-value streak (20+ days) ---
        if len(idx) > 40:  # ensure enough length
            start_i = np.random.randint(0, len(idx) - 25)
            streak_idx = idx[start_i:start_i + 22]
            df.loc[streak_idx, "temp"] = 15.0

    return df