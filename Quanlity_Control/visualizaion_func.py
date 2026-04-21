
import matplotlib.pyplot as plt

def plot_weather_data(df, title):
    """
    Plot temperature and precipitation time series.
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    
    axes[0].plot(df.index, df["temp"], color='#e63946', lw=0.8)
    axes[0].set_ylabel("Temperature (°C)")
    axes[0].set_title(title)
    
    axes[1].plot(df.index, df["precip"], color='#0081a7', lw=0.8)
    axes[1].set_ylabel("Precipitation (mm)")
    # axes[1].set_title(title)
    
    plt.tight_layout()
    plt.show()


def plot_timeseries_with_missing(
    df,
    missing_times,
    value_col=None,
    figsize=(12, 5),
    line_color='gray',
    missing_color='#e63946',
    alpha=0.6,
    lw=1.0,
    
    title="Time series with missing timestamps"
):
    """
    Plot time series with vertical lines marking missing timestamps.

    Parameters
    ----------
    df : pandas.DataFrame
        Time-indexed dataframe
    missing_times : array-like (DatetimeIndex or list)
        Missing timestamps
    value_col : str or None
        Column name to plot (if None, use first column)
    figsize : tuple
    line_color : str
    missing_color : str
    alpha : float
        Transparency for missing lines
    lw : float
        Line width for time series
    title : str
    """

    # select column
    if value_col is None:
        series = df.iloc[:, 0]
    else:
        series = df[value_col]

    fig, ax = plt.subplots(figsize=figsize)

    # plot time series
    ax.plot(series.index, series, color=line_color, lw=lw, label='Observed')

    # vertical lines for missing timestamps
    ax.vlines(
        x=missing_times,
        ymin=series.min(),
        ymax=series.max(),
        color=missing_color,
        alpha=alpha,
        label='Missing'
    )

    ax.set_title(title)
    ax.set_ylabel("Value")
    ax.legend()

    plt.show()

    # return fig, ax



def plot_out_range(df, min_val, max_val, flag=None):
    fig, ax = plt.subplots(figsize=(12,5))

    # main line
    ax.plot(df.index, df.iloc[:,0], color='gray', linewidth=1, label="Temperature")

    # out-of-range points
    if flag is not None:
        mask = flag.iloc[:,0] == 1
        ax.scatter(
            df.index[mask],
            df.iloc[:,0][mask],
            color='orange',
            s=10,
            label="Out of range"
        )


    ax.axhline(min_val, linestyle="--", color="#0081a7", alpha=0.5)
    ax.axhline(max_val, linestyle="--", color="#0081a7", alpha=0.5)

    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Ou-of-range Check: Temperature Time Series")
    ax.legend()

    plt.show()