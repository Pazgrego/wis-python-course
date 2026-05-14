"""
visualize.py - Matplotlib visualisation for Protein Thermal Shift Assay.

Produces a two-panel figure:
  Top panel    : Raw melting curves (fluorescence vs temperature) for both
                 conditions with vertical Tm markers.
  Bottom panel : First derivatives (dF/dT) showing the Tm peaks.
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

from analysis import load_data, add_derivatives, calculate_tm_values

# ── Output path ───────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_PNG = OUTPUT_DIR / "melting_curve_analysis.png"

# ── Palette ───────────────────────────────────────────────────────────────────
CLR_PROTEIN = "#2E86AB"        # steel blue  — protein only
CLR_LIGAND  = "#E84855"        # vivid red   — protein + ligand
CLR_TM_P    = "#2E86AB"
CLR_TM_L    = "#E84855"
CLR_BG      = "#F7F9FC"
CLR_GRID    = "#DDE3ED"


def build_figure(df, tm_results: dict) -> plt.Figure:
    """
    Construct and return the two-panel Matplotlib figure.

    Parameters
    ----------
    df         : DataFrame with raw + derivative columns (from add_derivatives).
    tm_results : dict from calculate_tm_values().
    """
    temp  = df["Temperature"].to_numpy()
    f_p   = df["Protein_Only"].to_numpy()
    f_l   = df["Protein_With_Ligand"].to_numpy()
    df_p  = df["dF_dT_Protein_Only"].to_numpy()
    df_l  = df["dF_dT_Protein_With_Ligand"].to_numpy()

    tm_p = tm_results["tm_protein_only"]
    tm_l = tm_results["tm_protein_with_ligand"]
    delta = tm_results["delta_tm"]

    # ── Figure layout ─────────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(10, 8),
        sharex=True,
        facecolor=CLR_BG,
        gridspec_kw={"hspace": 0.08, "height_ratios": [1, 1]},
    )

    for ax in (ax1, ax2):
        ax.set_facecolor(CLR_BG)
        ax.grid(color=CLR_GRID, linewidth=0.8, linestyle="--", zorder=0)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color("#AABBD0")

    # ── Panel 1 : Melting curves ──────────────────────────────────────────────
    ax1.plot(temp, f_p, color=CLR_PROTEIN, linewidth=2.2,
             label="Protein Only", zorder=3)
    ax1.plot(temp, f_l, color=CLR_LIGAND,  linewidth=2.2,
             label="Protein + Ligand", zorder=3)

    # Tm vertical lines
    _add_tm_marker(ax1, tm_p, f_p, temp, CLR_TM_P, label=f"Tm = {tm_p:.1f} °C")
    _add_tm_marker(ax1, tm_l, f_l, temp, CLR_TM_L, label=f"Tm = {tm_l:.1f} °C")

    ax1.set_ylabel("Fluorescence Intensity (RFU)", fontsize=11)
    ax1.set_title(
        "Protein Thermal Shift Assay — Melting Curve Analysis",
        fontsize=14, fontweight="bold", pad=14, color="#1A2533",
    )

    # Legend
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels, framealpha=0.9, edgecolor=CLR_GRID,
               fontsize=9.5, loc="upper right")

    # ── Panel 2 : First derivatives ───────────────────────────────────────────
    ax2.plot(temp, df_p, color=CLR_PROTEIN, linewidth=2.2,
             label="dF/dT  Protein Only", zorder=3)
    ax2.plot(temp, df_l, color=CLR_LIGAND,  linewidth=2.2,
             label="dF/dT  Protein + Ligand", zorder=3)

    # Peak markers (Tm points)
    idx_p = int(np.argmax(df_p))
    idx_l = int(np.argmax(df_l))

    ax2.scatter(temp[idx_p], df_p[idx_p], color=CLR_TM_P, s=90, zorder=5,
                edgecolors="white", linewidths=1.5)
    ax2.scatter(temp[idx_l], df_l[idx_l], color=CLR_TM_L, s=90, zorder=5,
                edgecolors="white", linewidths=1.5)

    ax2.axvline(tm_p, color=CLR_TM_P, linewidth=1.2, linestyle=":",
                alpha=0.75, zorder=2)
    ax2.axvline(tm_l, color=CLR_TM_L, linewidth=1.2, linestyle=":",
                alpha=0.75, zorder=2)

    # ΔTm bracket annotation
    y_bracket = max(df_p.max(), df_l.max()) * 0.55
    ax2.annotate(
        "", xy=(tm_l, y_bracket), xytext=(tm_p, y_bracket),
        arrowprops=dict(arrowstyle="<->", color="#555", lw=1.4),
    )
    ax2.text(
        (tm_p + tm_l) / 2, y_bracket * 1.08,
        f"ΔTm = {delta:+.1f} °C",
        ha="center", va="bottom", fontsize=10, color="#333",
        bbox=dict(boxstyle="round,pad=0.3", fc="white",
                  ec=CLR_GRID, alpha=0.9),
    )

    ax2.set_xlabel("Temperature (°C)", fontsize=11)
    ax2.set_ylabel("dF / dT", fontsize=11)
    ax2.legend(framealpha=0.9, edgecolor=CLR_GRID, fontsize=9.5,
               loc="upper right")

    # ── Shared x-axis ticks ───────────────────────────────────────────────────
    ax2.set_xlim(temp.min() - 0.5, temp.max() + 0.5)

    # ── Footer annotation ─────────────────────────────────────────────────────
    fig.text(
        0.5, 0.01,
        "First-derivative method  |  Tm identified at peak of dF/dT",
        ha="center", fontsize=8.5, color="#8899AA",
    )

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    return fig


# ── Helper ────────────────────────────────────────────────────────────────────

def _add_tm_marker(ax, tm, fluorescence, temperature, color, label):
    """Draw a vertical dashed line and star marker at Tm."""
    ax.axvline(tm, color=color, linewidth=1.3, linestyle="--",
               alpha=0.8, zorder=2)
    # Interpolate fluorescence at exact Tm
    y_val = float(np.interp(tm, temperature, fluorescence))
    ax.scatter([tm], [y_val], marker="*", s=180, color=color,
               edgecolors="white", linewidths=1, zorder=6,
               label=label)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = load_data()
    df = add_derivatives(df)
    tm_results = calculate_tm_values(df)

    fig = build_figure(df, tm_results)

    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight",
                facecolor=CLR_BG)
    print(f"Figure saved → {OUTPUT_PNG}")
    plt.show()
