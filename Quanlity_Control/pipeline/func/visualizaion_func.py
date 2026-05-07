import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_weather_data(df, color_map=None, title="Weather Data"):

    value_cols = ["temp", "tmin", "tmax",
                  "precip", "snw_fall", "snw_dpth"]

    # keep only columns that actually exist
    plot_cols = [col for col in value_cols if col in df.columns]

    # default colors
    if color_map is None:
        color_map = {}

    n_vars = len(plot_cols)

    fig, axes = plt.subplots(
        n_vars, 1,
        figsize=(12, 2.5 * n_vars),
        sharex=True
    )

    if n_vars == 1:
        axes = [axes]

    for ax, col in zip(axes, plot_cols):

        color = color_map.get(col, "gray")

        ax.plot(df.index, df[col],
                lw=0.8,
                color=color)

        ax.set_ylabel(col)

    axes[0].set_title(title)

    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt

def plot_timeseries_with_naught_missing_multi(
    df,
    color_map,
    naught_all=None,
    miss_result_dict=None,
    value_cols=None,
    figsize=(12, 2.5),
    alpha=0.6,
    lw=1.0,
    title="Time series with QC + missing"
):

    # print(naught_all.columns)
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

        y_min = series.min()
        y_max = series.max()
        offset = (y_max - y_min) * 0.05 if y_max > y_min else 1

        # =========================
        # QC flags (TOP)
        # =========================
        if naught_all is not None and col in naught_all.columns:

            qc_series = naught_all[col]

            flagged_times = naught_all.index[qc_series == 1]

            if len(flagged_times) > 0:
                ax.scatter(
                    flagged_times,
                    [y_max + offset] * len(flagged_times),
                    color="red",
                    marker="o",
                    s=15,
                    alpha=0.7,
                    label="QC flag"
                )

            n_flagged = qc_series.sum()

            ax.text(
                0.01, 0.95,
                f"{n_flagged} naught flags",
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle="round", alpha=0.2, color="red")
            )

        # =========================
        # Missing info (BELOW QC)
        # =========================
        if miss_result_dict is not None:

            miss_info = miss_result_dict.get(col, None)

            if miss_info is not None:

                missing_times = miss_info["missing_times"]
                n_missing = miss_info.get("n_missing", len(missing_times))
                missing_pct = miss_info.get("missing_pct", 0)

                if len(missing_times) > 0:
                    ax.scatter(
                        missing_times,
                        [y_min - offset] * len(missing_times),
                        color="gray",
                        marker="x",
                        alpha=alpha,
                        label="missing"
                    )

                ax.text(
                    0.01, 0.82,   # BELOW QC
                    f"{n_missing} missing ({missing_pct:.1f}%)",
                    transform=ax.transAxes,
                    fontsize=9,
                    verticalalignment='top',
                    bbox=dict(boxstyle="round", alpha=0.2)
                )

        # -------------------------
        # styling
        # -------------------------
        ax.set_ylabel(col)

        # clean legend duplicates
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc="upper right")

    axes[0].set_title(title)

    plt.tight_layout()
    plt.show()


def plot_out_range_single(df, min_val, max_val, flag=None, var_name=""):

    fig, ax = plt.subplots(figsize=(12,5))

    series = df.iloc[:, 0]

    ax.plot(series.index, series, color='gray', linewidth=1, label=var_name)

    if flag is not None:

        # ✅ handle both Series and DataFrame
        if isinstance(flag, pd.DataFrame):
            mask = flag.iloc[:, 0] == 1
        else:
            mask = flag == 1

        ax.scatter(
            series.index[mask],
            series[mask],
            color='orange',
            s=10,
            label="Out of range"
        )

    ax.axhline(min_val, linestyle="--", color="#0081a7", alpha=0.5)
    ax.axhline(max_val, linestyle="--", color="#0081a7", alpha=0.5)

    ax.set_ylabel(var_name)
    ax.set_title(f"Out-of-range Check: {var_name}")
    ax.legend()

    plt.show()


def plot_multi_range_check(
    df,
    wmo_rules,
    range_results,
    color_map,
    outrange_scatter_color,
    title = "WMO Range Check",
    figsize=(12, 2.8),
    lw=1.0,
    alpha=0.7
):

    vars_to_plot = [v for v in wmo_rules if v in df.columns]
    n = len(vars_to_plot)

    fig, axes = plt.subplots(n, 1, figsize=(figsize[0], figsize[1]*n), sharex=True)

    if n == 1:
        axes = [axes]

    for ax, var in zip(axes, vars_to_plot):

        series = df[var]
        bounds = wmo_rules[var]
        res = range_results[var]
        flag = res["flag"]

        var_color = color_map.get(var, "black")

        # -------------------------
        # main line (use color_map)
        # -------------------------
        ax.plot(
            series.index,
            series,
            color=var_color,
            lw=lw,
            label=var
        )

        # -------------------------
        # out-of-range points
        # -------------------------
        mask = flag == 1
        
        # Also flag negative values if min bound is None (for precip/snow variables)
        if bounds["min"] is None:
            negative_mask = series < 0
            mask = mask | negative_mask

        ax.scatter(
            series.index[mask],
            series[mask],
            color=outrange_scatter_color,   # keep consistent warning color
            s=10,
            alpha=alpha,
            label="Out of range"
        )

        # -------------------------
        # thresholds
        # -------------------------
        if bounds["min"] is not None:
            ax.axhline(
                bounds["min"],
                linestyle="--",
                color=var_color,
                alpha=0.4
            )

        if bounds["max"] is not None:
            ax.axhline(
                bounds["max"],
                linestyle="--",
                color=var_color,
                alpha=0.4
            )

        # -------------------------
        # summary stats
        # -------------------------
        if bounds["min"] is not None:
            n_below = (series < bounds["min"]).sum()
        else:
            # If no explicit min bound, check for negative values (invalid for precip/snow vars)
            n_below = (series < 0).sum()
        
        n_above = (series > bounds["max"]).sum() if bounds["max"] is not None else 0
        n_total = mask.sum()

        text = (
            f"flagged: {n_total}\n"
            f"below_min: {n_below}\n"
            f"above_max: {n_above}"
        )

        ax.text(
            0.01, 0.95,
            text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", alpha=0.2)
        )

        # -------------------------
        # styling
        # -------------------------
        ax.set_ylabel(var)
        ax.legend(loc="upper right")

    axes[0].set_title(title)

    plt.tight_layout()
    plt.show()


def plot_clim_check_multi(
    df,
    color_map,
    gap_flags=None,
    clim_flags=None,
    show_gap=True,
    show_clim=True,
    hide_flagged=False,
    figsize=(12, 2.5),
    title = "QC Check (Gap + Climatological)",
):

    cols = gap_flags.columns
    n = len(cols)

    fig, axes = plt.subplots(n, 1, figsize=(figsize[0], figsize[1]*n), sharex=True)

    if n == 1:
        axes = [axes]

    for ax, col in zip(axes, cols):

        series = df[col].copy()
        color = color_map.get(col, "gray")

        # -------------------------
        # combine flags
        # -------------------------
        combined_flag = pd.Series(False, index=df.index)

        if gap_flags is not None and col in gap_flags.columns:
            combined_flag |= gap_flags[col]

        if clim_flags is not None and col in clim_flags.columns:
            combined_flag |= clim_flags[col]

        # -------------------------
        # optionally hide flagged values
        # -------------------------
        if hide_flagged:
            series = series.where(~combined_flag)

        # -------------------------
        # plot main line
        # -------------------------
        ax.plot(series.index, series, color=color, lw=0.8, label=col)

        # -------------------------
        # gap flags
        # -------------------------
        if show_gap and gap_flags is not None and col in gap_flags.columns:

            mask = gap_flags[col]

            if mask.sum() > 0:
                ax.scatter(
                    df.index[mask],
                    df[col][mask],
                    color="#a98467",
                    s=15,
                    label="Gap",
                    marker="s",

                )

        # -------------------------
        # climatological flags
        # -------------------------
        if show_clim and clim_flags is not None and col in clim_flags.columns:

            mask = clim_flags[col]

            if mask.sum() > 0:
                ax.scatter(
                    df.index[mask],
                    df[col][mask],
                    color="#778da9",
                    s=15,
                    label="Clim",
                    marker="x",
                )

        # -------------------------
        # summary text
        # -------------------------
        text_lines = []

        if gap_flags is not None and col in gap_flags.columns:
            text_lines.append(f"gap: {gap_flags[col].sum()}")

        if clim_flags is not None and col in clim_flags.columns:
            text_lines.append(f"clim: {clim_flags[col].sum()}")

        if text_lines:
            ax.text(
                0.01, 0.82,
                "\n".join(text_lines),
                transform=ax.transAxes,
                fontsize=9,
                bbox=dict(boxstyle="round", alpha=0.2)
            )

        # -------------------------
        # styling
        # -------------------------
        ax.set_ylabel(col)

        # clean legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc = 'upper right')

    axes[0].set_title(title)

    plt.tight_layout()
    plt.show()



def plot_inttemp_tas_timeseries(
    daily_cleaned, 
    inttemp_tas_result,
    color_map,
    missing_color,
    state_color,
    title="Internal and temporal consistency checks - Temp, TMAX, TMIN"
):
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # ----------------------------
    # TOP: temperature time series
    # ----------------------------
    axes[0].plot(
        daily_cleaned.index, daily_cleaned["temp"],
        label="Temp",
        lw=0.8,
        color=color_map.get("temp", "black")
    )

    axes[0].plot(
        daily_cleaned.index, daily_cleaned["tmax"],
        label="Tmax",
        lw=0.8,
        color=color_map.get("tmax", "black")
    )

    axes[0].plot(
        daily_cleaned.index, daily_cleaned["tmin"],
        label="Tmin",
        lw=0.8,
        color=color_map.get("tmin", "black")
    )

    axes[0].set_ylabel("Temperature (°C)")
    axes[0].set_title(title)

    # ----------------------------
    # overlay QC flags
    # ----------------------------
    for label, marker in zip(["suspect", "bad"], ["o", "x"]):
        subset = inttemp_tas_result[inttemp_tas_result["qc_label"] == label]
        axes[0].scatter(
            subset.index,
            subset["temp"],
            label=label,
            marker=marker,
            s=20,
            color="red" if label == "bad" else "orange"
        )

    ymin = daily_cleaned[["tmin", "temp", "tmax"]].min().min()
    subset = inttemp_tas_result[inttemp_tas_result["qc_label"] == "missing"]

    axes[0].scatter(
        subset.index,
        [ymin - 2] * len(subset),
        marker="s",
        s=20,
        color=missing_color,
        label="missing"
    )

    axes[0].legend()

    # ----------------------------
    # BOTTOM: QC state timeline
    # ----------------------------
    axes[1].plot(
        inttemp_tas_result.index,
        inttemp_tas_result["qc_code"],
        drawstyle="steps-mid",
        color=state_color
    )

    axes[1].set_ylabel("QC Code")
    axes[1].set_yticks([0, 1, 2, 3])
    axes[1].set_yticklabels(["missing", "good", "suspect", "bad"])

    plt.tight_layout()
    plt.show()


def plot_inttemp_snow_tmin_timeseries(
    df,
    snow_temp_qc,
    color_map,
    missing_color,
    state_color,
    title="Snow–Temperature QC Check"
):

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # --------------------------------------------------
    # TOP: physical variables
    # --------------------------------------------------
    axes[0].plot(
        df.index, df["snw_fall"],
        label="Snowfall",
        lw=0.8,
        color=color_map.get("snw_fall", "black")
    )

    axes[0].plot(
        df.index, df["snw_dpth"],
        label="Snow Depth",
        lw=0.8,
        color=color_map.get("snw_dpth", "black")
    )

    axes[0].plot(
        df.index, df["tmin"],
        label="Tmin",
        lw=0.8,
        color=color_map.get("tmin", "black")
    )

    axes[0].set_ylabel("Values")
    axes[0].set_title(title)

    # --------------------------------------------------
    # QC flags
    # --------------------------------------------------
    snow_flag = snow_temp_qc["flag_snow_warm"]
    snwd_flag = snow_temp_qc["flag_snwd_warm"]

    f_snow = snow_flag.fillna(False)
    f_snwd = snwd_flag.fillna(False)

    # flagged points
    axes[0].scatter(
        df.index[f_snow],
        df.loc[f_snow, "snw_fall"],
        marker="o",
        s=25,
        color="orange",
        label="snow_warm"
    )

    axes[0].scatter(
        df.index[f_snwd],
        df.loc[f_snwd, "snw_dpth"],
        marker="x",
        s=25,
        color="red",
        label="snwd_warm"
    )

    axes[0].axhline(7, color = '#d6ccc2', label = "7°C")
    # --------------------------------------------------
    # missing QC
    # --------------------------------------------------
    missing = snow_flag.isna() | snwd_flag.isna()

    if missing.any():
        ymin = np.nanmin(df[["snw_fall", "snw_dpth", "tmin"]].values)

        axes[0].scatter(
            df.index[missing],
            [ymin - 1] * missing.sum(),
            marker="s",
            s=20,
            color=missing_color,
            label="missing"
        )

    axes[0].legend()

    # --------------------------------------------------
    # BOTTOM: TWO QC timelines (stacked style)
    # --------------------------------------------------

    # convert flags safely to numeric
    snow_num = snow_flag.map({True: 2, False: 1})
    snwd_num = snwd_flag.map({True: 2, False: 1})

    # missing handling
    snow_num = snow_num.fillna(0)
    snwd_num = snwd_num.fillna(0)

    # vertical separation (key fix)
    snow_offset = 0
    snwd_offset = 2.5

    axes[1].plot(
        df.index,
        snow_num + snow_offset,
        drawstyle="steps-mid",
        color=state_color[0],
        label="snow_warm"
    )

    axes[1].plot(
        df.index,
        snwd_num + snwd_offset,
        drawstyle="steps-mid",
        color=state_color[1],
        label="snwd_warm"
    )

    axes[1].set_yticks([0, 1, 2, 2.5, 3.5, 4.5])
    axes[1].set_yticklabels([
        "snow: missing", "snow: ok", "snow: flag",
        "snwd: missing", "snwd: ok", "snwd: flag"
    ])

    axes[1].set_title("QC Timeline")
    axes[1].legend()

    plt.tight_layout()
    plt.show()


def plot_inttemp_snow_fall_dpth_timeseries(
    df,
    snow_qc,
    color_map,
    missing_color,
    state_color,
    title="Snow QC Check"
):

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # --------------------------------------------------
    # TOP: physical variables
    # --------------------------------------------------
    axes[0].plot(
        df.index, df["snw_fall"],
        label="Snowfall",
        lw=0.8,
        color=color_map.get("snw_fall", "black")
    )

    axes[0].plot(
        df.index, df["snw_dpth"],
        label="Snow Depth",
        lw=0.8,
        color=color_map.get("snw_dpth", "black")
    )

    axes[0].set_ylabel("Snow Variables")
    axes[0].set_title(title)

    # --------------------------------------------------
    # QC FLAGS
    # --------------------------------------------------
    flag_col = snow_qc["flag_snow_snwd"]

    # encode: 0 = missing, 1 = ok, 2 = flag
    flag_num = flag_col.map({False: 1, True: 2}).fillna(0)

    flagged = flag_num == 2
    missing = flag_col.isna()

    # --------------------------------------------------
    # TOP PANEL: flagged points
    # --------------------------------------------------
    axes[0].scatter(
        df.index[flagged],
        df.loc[flagged, "snw_fall"],
        marker="x",
        s=20,
        color=state_color[1] if isinstance(state_color, (list, tuple)) else state_color,
        label="flagged"
    )

    axes[0].scatter(
        df.index[flagged],
        df.loc[flagged, "snw_dpth"],
        marker="x",
        s=20,
        color=state_color[1] if isinstance(state_color, (list, tuple)) else state_color
    )

    # missing QC
    if missing.any():
        ymin = np.nanmin(df[["snw_fall", "snw_dpth"]].values)

        axes[0].scatter(
            df.index[missing],
            [ymin - 5] * missing.sum(),
            marker="s",
            s=20,
            color=missing_color,
            label="missing"
        )

    axes[0].legend()

    # --------------------------------------------------
    # BOTTOM: QC timelines (snow + snwd_prev)
    # --------------------------------------------------

    # encode QC states
    snow_num = snow_qc["flag_snow_snwd"].map({False: 1, True: 2})
    snwd_num = snow_qc["flag_snwd_prev"].map({False: 1, True: 2})

    snow_num = snow_num.fillna(0)
    snwd_num = snwd_num.fillna(0)

    # vertical separation (key idea)
    snow_offset = 0
    snwd_offset = 2.5

    # snow QC line
    axes[1].plot(
        df.index,
        snow_num + snow_offset - 0.5,
        drawstyle="steps-mid",
        color=state_color[0] if isinstance(state_color, (list, tuple)) else state_color,
        label="snow QC"
    )

    # snwd_prev QC line
    axes[1].plot(
        df.index,
        snwd_num + snwd_offset - 0.5,
        drawstyle="steps-mid",
        color=state_color[1] if isinstance(state_color, (list, tuple)) else state_color,
        label="snwd_prev QC"
    )

    # --------------------------------------------------
    # axis formatting
    # --------------------------------------------------
    axes[1].set_ylabel("QC State")

    axes[1].set_yticks([
        -0.5, 0.5, 1.5,      # snow band
        2.0, 3.0, 4.0        # snwd_prev band
    ])

    axes[1].set_yticklabels([
        "snow: missing", "snow: ok", "snow: flag",
        "snwd: missing", "snwd: ok", "snwd: flag"
    ])

    axes[1].set_title("QC Timeline (snow + lagged snow depth)")
    axes[1].legend()


    plt.tight_layout()
    plt.show()
    


def plot_inttemp_snow_precip_timeseries(
    df,
    snow_precip_qc,
    color_map,
    missing_color,
    state_color,
    title="Snow–Precipitation QC Check"
):

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # --------------------------------------------------
    # TOP: physical variables
    # --------------------------------------------------
    axes[0].plot(
        df.index, df["snw_fall"],
        label="Snowfall",
        lw=0.8,
        color=color_map.get("snw_fall", "black")
    )

    axes[0].plot(
        df.index, df["snw_dpth"],
        label="Snow Depth",
        lw=0.8,
        color=color_map.get("snw_dpth", "black")
    )

    axes[0].plot(
        df.index, df["precip"],
        label="Precip",
        lw=0.8,
        color=color_map.get("precip", "gray")
    )

    axes[0].set_ylabel("Values")
    axes[0].set_title(title)

    # --------------------------------------------------
    # helper
    # --------------------------------------------------
    def to_num(flag):
        return flag.map({True: 1, False: 0})

    # --------------------------------------------------
    # flag groups (now using color_map + state_color)
    # --------------------------------------------------
    flag_groups = [
        ("flag_snow_no_prcp", "o",
         state_color[0], "snow_no_prcp", "snw_fall"),

        ("flag_snow_prcp_ratio", "x",
         state_color[1], "snow_ratio", "snw_fall"),

        ("flag_snwd_no_prcp", "o",
         state_color[2], "snwd_no_prcp", "snw_dpth"),

        ("flag_snwd_prcp_ratio", "x",
         state_color[3], "snwd_ratio", "snw_dpth"),
    ]

    # --------------------------------------------------
    # TOP: flagged points
    # --------------------------------------------------
    for col, marker, color, label, var in flag_groups:
        flag = to_num(snow_precip_qc[col])
        f = flag == 1

        axes[0].scatter(
            df.index[f],
            df.loc[f, var],
            marker=marker,
            s=25,
            color=color,
            label=label
        )

    # missing QC
    missing = snow_precip_qc["flag_missing_any"] == 1

    if missing.any():
        ymin = np.nanmin(df[["snw_fall", "snw_dpth", "precip"]].values)

        axes[0].scatter(
            df.index[missing],
            [ymin - 10] * missing.sum(),
            marker="s",
            s=20,
            color=missing_color,
            label="missing QC"
        )

    axes[0].legend(ncol=2)

    # --------------------------------------------------
    # BOTTOM: stacked QC timeline
    # --------------------------------------------------
    y_offset = 0
    yticks = []
    ylabels = []

    for col, _, color, label, _ in flag_groups:
        flag = to_num(snow_precip_qc[col])

        y = flag.fillna(-0.5) + y_offset

        axes[1].plot(
            df.index,
            y,
            drawstyle="steps-mid",
            color=color,
            label=label
        )

        yticks.extend([y_offset - 0.5, y_offset, y_offset + 1])
        ylabels.extend(["missing", "ok", "flag"])

        y_offset += 1.8

    axes[1].set_ylabel("QC State")
    axes[1].set_yticks(yticks)
    axes[1].set_yticklabels(ylabels)
    axes[1].set_title("QC Timeline")
    axes[1].legend(ncol=2)

    plt.tight_layout()
    plt.show()


def plot_station_qc(
    station_id,
    daily_all,
    daily_cleaned,
    result,
    value_cols,
    color_map,
    plots=None
):
    """
    Plot selected QC diagnostics for one station.

    Parameters
    ----------
    station_id : int or str
        Station ID

    daily_all : DataFrame
        Raw daily data

    daily_cleaned : DataFrame
        Cleaned daily data

    result : dict
        Output from run_qc_result_pipeline()

    value_cols : list
        Variable columns

    color_map : dict
        Variable color mapping

    plots : list or None
        Which plots to generate.
        If None -> plot everything.

        Available options:
        ------------------
        "raw"
        "naught_missing"
        "range"
        "cleaned"
        "clim"
        "inttemp_tas"
        "inttemp_snow_tmin"
        "inttemp_snow_fall_dpth"
        "inttemp_snow_precip"
    """

    # --------------------------------------------------
    # Default: plot everything
    # --------------------------------------------------
    if plots is None:
        plots = [
            "raw",
            "naught_missing",
            "range",
            "cleaned",
            "clim",
            "inttemp_tas",
            "inttemp_snow_tmin",
            "inttemp_snow_fall_dpth",
            "inttemp_snow_precip"
        ]

    # --------------------------------------------------
    # Raw data
    # --------------------------------------------------
    if "raw" in plots:
        plot_weather_data(
            daily_all,
            color_map=color_map,
            title=f"Station {station_id}: raw daily data"
        )

    # --------------------------------------------------
    # Naught + missing
    # --------------------------------------------------
    if "naught_missing" in plots:
        plot_timeseries_with_naught_missing_multi(
            df=daily_all,
            color_map=color_map,
            naught_all=result["naught_all"],
            miss_result_dict=result["miss_result_dict"],
            value_cols=value_cols,
            title=f"Station {station_id}: raw daily series with naught + missing flags"
        )

    # --------------------------------------------------
    # Range check
    # --------------------------------------------------
    if "range" in plots:
        plot_multi_range_check(
            df=daily_all,
            wmo_rules=result["wmo_rules"],
            range_results=result["range_results"],
            color_map=color_map,
            outrange_scatter_color="#843939",
            title=f"Station {station_id}: WMO Range Check"
        )

    # --------------------------------------------------
    # Cleaned data
    # --------------------------------------------------
    if "cleaned" in plots:
        plot_weather_data(
            daily_cleaned,
            color_map=color_map,
            title=f"Station {station_id}: cleaned daily data"
        )

    # --------------------------------------------------
    # Gap + climatology
    # --------------------------------------------------
    if "clim" in plots:

        gap_flags = (
            pd.concat(
                {col: res["flag"] for col, res in result["gap_result_dict"].items()},
                axis=1
            )
            if result["gap_result_dict"]
            else pd.DataFrame(index=daily_all.index)
        )

        plot_clim_check_multi(
            df=daily_cleaned,
            color_map=color_map,
            gap_flags=gap_flags,
            clim_flags=result["clim_flag_df"],
            show_gap=True,
            show_clim=True,
            title=f"Station {station_id}: Climatological check"
        )

    # --------------------------------------------------
    # Temperature internal consistency
    # --------------------------------------------------
    if "inttemp_tas" in plots:
        plot_inttemp_tas_timeseries(
            daily_cleaned,
            result["inttemp_tas_result"],
            color_map=color_map,
            missing_color="gray",
            state_color="#7d4f50",
            title=f"Station {station_id}: temperature internal consistency"
        )

    # --------------------------------------------------
    # Snow-temperature consistency
    # --------------------------------------------------
    if "inttemp_snow_tmin" in plots:
        plot_inttemp_snow_tmin_timeseries(
            daily_cleaned,
            result["inttemp_snow_tmin_result"],
            color_map=color_map,
            missing_color="gray",
            state_color=["#7d4f50", "#6b705c"],
            title=f"Station {station_id}: snow–temperature consistency"
        )

    # --------------------------------------------------
    # Snowfall-snow depth consistency
    # --------------------------------------------------
    if "inttemp_snow_fall_dpth" in plots:
        plot_inttemp_snow_fall_dpth_timeseries(
            daily_cleaned,
            result["inttemp_snow_fall_dpth_result"],
            color_map=color_map,
            missing_color="gray",
            state_color=["#7d4f50", "#6b705c"],
            title=f"Station {station_id}: snowfall–snow depth consistency"
        )

    # --------------------------------------------------
    # Snow-precipitation consistency
    # --------------------------------------------------
    if "inttemp_snow_precip" in plots:
        plot_inttemp_snow_precip_timeseries(
            daily_cleaned,
            result["inttemp_snow_precip_result"],
            color_map=color_map,
            missing_color="gray",
            state_color=["#7d4f50", "#6b705c", "#cb997e", "#415a77"],
            title=f"Station {station_id}: snow–precipitation consistency"
        )

