
import matplotlib.pyplot as plt
import pandas as pd

def plot_weather_data(df, color_map=None, title="Weather Data"):

    # default to gray if no color_map provided
    if color_map is None:
        color_map = {}

    n_vars = len(df.columns)
    fig, axes = plt.subplots(n_vars, 1, figsize=(12, 2.5 * n_vars), sharex=True)

    if n_vars == 1:
        axes = [axes]

    for ax, col in zip(axes, df.columns):

        color = color_map.get(col, "gray")  # fallback always gray

        ax.plot(df.index, df[col], lw=0.8, color=color)
        ax.set_ylabel(col)

    axes[0].set_title(title)

    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt

def plot_timeseries_with_naught_missing_multi(
    df,
    color_map,
    naught_all=None,
    naught_map=None,
    miss_result_dict=None,
    value_cols=None,
    figsize=(12, 2.5),
    alpha=0.6,
    lw=1.0,
    title="Time series with QC + missing"
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

        y_min = series.min()
        y_max = series.max()
        offset = (y_max - y_min) * 0.05 if y_max > y_min else 1

        # =========================
        # QC flags (TOP)
        # =========================
        if naught_all is not None and naught_map is not None:

            qc_col = naught_map.get(col, None)

            if qc_col in naught_all.columns:

                flagged_times = naught_all.index[naught_all[qc_col]]

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

                n_flagged = naught_all[qc_col].sum()

                ax.text(
                    0.01, 0.95,   # TOP
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

        # -------------------------
        # main line
        # -------------------------
        ax.plot(series.index, series, color="gray", lw=lw)

        # -------------------------
        # out-of-range points
        # -------------------------
        mask = flag == 1

        ax.scatter(
            series.index[mask],
            series[mask],
            color="orange",
            s=10,
            alpha=alpha,
            label="Out of range"
        )

        # -------------------------
        # thresholds
        # -------------------------
        ax.axhline(bounds["min"], linestyle="--", color="#0081a7", alpha=0.5)
        ax.axhline(bounds["max"], linestyle="--", color="#0081a7", alpha=0.5)

        # -------------------------
        # summary stats
        # -------------------------
        n_below = (series < bounds["min"]).sum()
        n_above = (series > bounds["max"]).sum()
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

    axes[0].set_title("WMO Range Check (All Variables)")

    plt.tight_layout()
    plt.show()


def plot_gap_multi(df, gap_flags, color_map, figsize=(12, 2.5)):

    cols = gap_flags.columns
    n = len(cols)

    fig, axes = plt.subplots(n, 1, figsize=(figsize[0], figsize[1]*n), sharex=True)

    if n == 1:
        axes = [axes]

    for ax, col in zip(axes, cols):

        series = df[col]
        color = color_map.get(col, "gray")

        # main line
        ax.plot(series.index, series, color=color, lw=0.8, label=col)

        # flagged points
        mask = gap_flags[col]

        if mask.sum() > 0:
            ax.scatter(
                series.index[mask],
                series[mask],
                color="darkred",
                s=15,
                label="Gap flagged"
            )

        # summary text
        ax.text(
            0.01, 0.9,
            f"{mask.sum()} gap flags",
            transform=ax.transAxes,
            fontsize=9,
            bbox=dict(boxstyle="round", alpha=0.2)
        )

        ax.set_ylabel(col)
        ax.legend()

    axes[0].set_title("Gap Check (All Variables)")
    plt.tight_layout()
    plt.show()


import matplotlib.pyplot as plt
import numpy as np

def plot_clim_check_multi(
    df,
    color_map,
    gap_flags=None,
    clim_flags=None,
    show_gap=True,
    show_clim=True,
    hide_flagged=False,
    figsize=(12, 2.5)
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

    axes[0].set_title("QC Check (Gap + Climatological)")

    plt.tight_layout()
    plt.show()