# Day 05 — Protein Thermal Shift Assay (TSA) Analysis

## Overview

This project implements a complete analysis pipeline for **Differential Scanning Fluorimetry (DSF)**, also called a **Protein Thermal Shift Assay (TSA)**. The goal is to identify the **Melting Temperature (Tm)** of a protein — the temperature at which half the protein population is unfolded — using the **first-derivative method**, and to detect ligand-induced stabilisation by comparing Tm values between conditions.

---

## How to run this project (step by step)

Do these steps **in order** from a terminal.

### Step 1 — Open the project folder

```bash
cd Day5
```

(Use the path to this folder on your machine if you are not already inside the course repo.)

**Stay in this folder** for Steps 2–6.

### Step 2 — Install Python packages

```bash
pip install -r requirements.txt
```

### Step 3 — Put the data file in the right place

The scripts read the CSV from **exactly** this path:

`Day5/data/melting_data.csv`

- If your CSV is somewhere else, **move or copy** it into the `data` folder and name it `melting_data.csv`.
- If the `data` folder does not exist, create it: `mkdir -p data`, then add the file.

### Step 4 — Run the analysis (prints Tm and ΔTm)

```bash
python analysis.py
```

You should see a short table in the terminal with Tm for each condition and whether the ligand stabilises the protein.

### Step 5 — Make the figure (optional)

```bash
python visualize.py
```

This creates **`data/melting_curve_analysis.png`** (melting curves and derivatives).

**If `visualize.py` crashes or hangs** (common in remote servers, CI, or some sandboxes), run it with a non-interactive Matplotlib backend and a writable config folder:

```bash
export MPLBACKEND=Agg
export MPLCONFIGDIR="$(pwd)/.mplcache"
mkdir -p "$MPLCONFIGDIR"
python visualize.py
```

You can ignore a warning that the figure cannot be “shown”; the PNG is still saved.

### Step 6 — Run the tests (optional)

```bash
python -m pytest test_logic.py -v
```

All tests should pass. They use synthetic curves, not your CSV.

---

## Background: What Is a Protein Thermal Shift Assay?

In a TSA experiment:
1. A protein is mixed with a fluorescent dye (e.g., SYPRO Orange) that fluoresces when bound to **hydrophobic residues**.
2. The sample is slowly heated while fluorescence is recorded.
3. As the protein **unfolds**, hydrophobic regions become exposed → fluorescence rises sharply.
4. At high temperatures, the protein aggregates and dye is released → fluorescence drops.

The resulting curve is a **sigmoid** (S-shaped). The **inflection point** of this sigmoid — where the rate of change is highest — is the **Tm**.

---

## What Is ΔTm and Why Does It Matter?

| Condition | Tm |
|---|---|
| Protein Only | Tm₀ |
| Protein + Ligand | Tm₁ |

**ΔTm = Tm₁ − Tm₀**

| ΔTm | Interpretation |
|---|---|
| **ΔTm > 0** | Ligand **stabilises** the protein (raises unfolding energy barrier) |
| **ΔTm < 0** | Ligand **destabilises** the protein |
| **ΔTm ≈ 0** | No significant interaction detected |

A positive ΔTm is a key early indicator in **drug discovery**: it suggests the ligand binds to and stabilises the target protein, which is a hallmark of a genuine protein-ligand interaction.

---

## First-Derivative Method

Instead of fitting a full sigmoid model, we use a simpler numerical approach:

```
dF/dT = first derivative of fluorescence with respect to temperature
Tm    = temperature at max(dF/dT)
```

**Why?**
- No model assumptions required.
- Robust against baseline drift.
- Computationally simple (numpy.gradient).
- Works even when curves are not perfectly sigmoidal.

---

## Project Structure

```
Day5/
├── data/
│   ├── melting_data.csv            # Raw fluorescence vs temperature
│   └── melting_curve_analysis.png  # Generated figure (after running visualize.py)
├── logic.py                        # Core maths: derivative + Tm finder
├── analysis.py                     # Pandas pipeline: load, process, compare
├── visualize.py                    # Matplotlib: melting curves + derivatives
├── test_logic.py                   # Pytest unit tests with synthetic data
├── requirements.txt
└── README.md
```

---

## Installation (same as Step 2 above)

```bash
cd Day5
pip install -r requirements.txt
```

---

## Usage (short reference)

| What you want | Command |
|----------------|---------|
| Tm summary in the terminal | `python analysis.py` |
| Save the plot as PNG | `python visualize.py` → `data/melting_curve_analysis.png` |
| Check the code with tests | `python -m pytest test_logic.py -v` |

See **How to run this project** at the top for full steps, the data path, and troubleshooting for plotting.

---

## Module Summary

### `logic.py`
| Function | Purpose |
|---|---|
| `compute_first_derivative(temp, fluor)` | Returns dF/dT via numpy central differences |
| `find_tm(temp, fluor)` | Returns Tm (°C) as temperature at peak dF/dT |
| `smooth_signal(fluor, window)` | Moving-average smoother to reduce noise |

### `analysis.py`
| Function | Purpose |
|---|---|
| `load_data(csv_path)` | Load & validate the CSV into a DataFrame |
| `add_derivatives(df)` | Append dF/dT columns to DataFrame |
| `calculate_tm_values(df)` | Return dict: Tm₀, Tm₁, ΔTm, stabilised flag |
| `print_summary(tm_results)` | Pretty-print the Tm report |

### `visualize.py`
| Function | Purpose |
|---|---|
| `build_figure(df, tm_results)` | Construct two-panel Matplotlib figure |

---

## Interpreting the Output Figure

- **Top panel** — raw fluorescence curves. Vertical dashed lines and ★ markers show each Tm.
- **Bottom panel** — first derivatives (dF/dT). Peaks visually confirm the Tm; the ΔTm bracket shows the thermal shift.

---

## Key Concept Summary

> A **rightward shift** of the melting curve (positive ΔTm) means the ligand makes the protein harder to unfold — it raises the thermodynamic stability. This is the core readout in **fragment screening**, **hit validation**, and **buffer optimisation** workflows in structural biology and drug discovery.
