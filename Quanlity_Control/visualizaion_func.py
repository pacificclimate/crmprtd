import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import pandas as pd

def plot_missing_periods(df, title="Time series with missing periods", 
                         series_label="Observed", color_series="gray", 
                         color_missing="red", alpha_missing=0.3, figsize=(12,5)):
    """
    Plot a time series and highlight missing timestamps or consecutive missing periods.

    Parameters
    ----------
    df : pd.DataFrame or pd.Series
        Time series with DatetimeIndex. If DataFrame, the first column is used.
    title : str
        Plot title.
    series_label : str
        Label for the observed series.
    color_series : str
        Color for the observed time series.
    color_missing : str
        Color for missing periods.
    alpha_missing : float
        Transparency for missing regions.
    figsize : tuple
        Figure size.
    """
    # Convert DataFrame to Series if needed
    if isinstance(df, pd.DataFrame):
        series = df.iloc[:,0]
    else:
        series = df

    fig, ax = plt.subplots(figsize=figsize)

    # Plot the observed series
    ax.plot(series.index, series.values, color=color_series, lw=0.5, label=series_label)

    # Detect missing points
    missing_mask = series.isna()
    groups = (missing_mask != missing_mask.shift()).cumsum()

    # Highlight missing periods
    for _, g in series.groupby(groups):
        if g.isna().all():
            ax.axvspan(
                g.index.min(),
                g.index.max(),
                color=color_missing,
                alpha=alpha_missing,
                lw=0,
                zorder=2
            )

    ax.set_title(title)
    ax.set_ylabel("Value")
    ax.legend()
    plt.show()
    