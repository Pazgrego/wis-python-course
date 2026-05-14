"""
analysis.py - Data loading, processing, and Tm comparison using Pandas.

Loads the melting curve CSV, calculates Tm for each condition via the
first-derivative method, and reports the thermal shift (ΔTm) that indicates
ligand-induced protein stabilisation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from logic import find_tm, compute_first_derivative, smooth_signal


# ── Path helpers ─────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_CSV = DATA_DIR / "melting_data.csv"


# ── Data I/O ─────────────────────────────────────────────────────────────────

def load_data(csv_path: Path = DEFAULT_CSV) -> pd.DataFrame:
    """
    Load the melting-curve CSV into a tidy DataFrame.

    Expected columns
    ----------------
    Temperature        : float  — temperature in °C
    Protein_Only       : float  — fluorescence without ligand
    Protein_With_Ligand: float  — fluorescence with ligand

    Returns
    -------
    pd.DataFrame with the three columns above, sorted by Temperature.
    """
    required = {"Temperature", "Protein_Only", "Protein_With_Ligand"}
    df = pd.read_csv(csv_path)

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required column(s): {missing}")

    df = df.sort_values("Temperature").reset_index(drop=True)
    return df


# ── Derivative enrichment ─────────────────────────────────────────────────────

def add_derivatives(df: pd.DataFrame, smooth: bool = True) -> pd.DataFrame:
    """
    Add first-derivative columns to the DataFrame.

    Parameters
    ----------
    df     : DataFrame from load_data()
    smooth : If True, apply a 5-point moving-average before differentiation
             to reduce noise artefacts.

    Returns
    -------
    Original DataFrame with two new columns:
        dF_dT_Protein_Only        : dF/dT for protein-only condition
        dF_dT_Protein_With_Ligand : dF/dT for protein + ligand condition
    """
    temp = df["Temperature"].to_numpy()

    for col in ("Protein_Only", "Protein_With_Ligand"):
        signal = df[col].to_numpy()
        if smooth:
            signal = smooth_signal(signal, window=5)
        _, deriv = compute_first_derivative(temp, signal)
        df[f"dF_dT_{col}"] = deriv

    return df


# ── Tm analysis ───────────────────────────────────────────────────────────────

def calculate_tm_values(df: pd.DataFrame, smooth: bool = True) -> dict:
    """
    Calculate Tm for both conditions and report the thermal shift.

    Parameters
    ----------
    df     : DataFrame (raw, before add_derivatives).
    smooth : Smooth signal before differentiation.

    Returns
    -------
    dict with keys:
        tm_protein_only         : float — Tm without ligand (°C)
        tm_protein_with_ligand  : float — Tm with ligand (°C)
        delta_tm                : float — ΔTm = Tm(+ligand) − Tm(−ligand)
        stabilised              : bool  — True when ΔTm > 0
    """
    temp = df["Temperature"].to_numpy()

    results = {}
    for label, col in [
        ("tm_protein_only", "Protein_Only"),
        ("tm_protein_with_ligand", "Protein_With_Ligand"),
    ]:
        signal = df[col].to_numpy()
        if smooth:
            signal = smooth_signal(signal, window=5)
        results[label] = find_tm(temp, signal)

    delta = results["tm_protein_with_ligand"] - results["tm_protein_only"]
    results["delta_tm"] = round(delta, 2)
    results["stabilised"] = delta > 0

    return results


# ── Pretty report ─────────────────────────────────────────────────────────────

def print_summary(tm_results: dict) -> None:
    """Print a formatted summary of Tm values and the thermal shift."""
    sep = "─" * 48
    print(sep)
    print("  Protein Thermal Shift Assay — Tm Summary")
    print(sep)
    print(f"  Tm (Protein Only)       : {tm_results['tm_protein_only']:.1f} °C")
    print(f"  Tm (Protein + Ligand)   : {tm_results['tm_protein_with_ligand']:.1f} °C")
    print(f"  ΔTm                     : {tm_results['delta_tm']:+.2f} °C")

    if tm_results["stabilised"]:
        print("  Interpretation          : ✓ Ligand STABILISES the protein")
    else:
        print("  Interpretation          : ✗ Ligand DESTABILISES the protein")
    print(sep)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = load_data()
    df = add_derivatives(df)

    print("\nData preview (first 5 rows):")
    print(df.head().to_string(index=False))
    print()

    tm_results = calculate_tm_values(df)
    print_summary(tm_results)
