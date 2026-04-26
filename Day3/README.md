# Day 3 — Dilution Calculator

## Project Overview

This tool calculates the exact volumes needed to prepare a diluted solution from a concentrated stock, using the standard biochemistry formula:

```
C1 × V1 = C2 × V2
```

| Symbol | Meaning |
|--------|---------|
| C1 | Stock (starting) concentration |
| C2 | Desired (final) concentration |
| V2 | Desired final volume |
| V1 | Volume of stock to pipette |

Given C1, C2, and V2, the calculator returns:
- **Stock to take** (V1)
- **Diluent to add** (V2 − V1)

This is an everyday calculation in molecular biology, genomics, and any wet-lab setting.

---

## File Structure

```
Day3/
├── logic.py          # Core calculation (calculate_dilution)
├── ui_input.py       # Interactive prompt interface
├── ui_cli.py         # Command-line argument interface
├── ui_gui.py         # Tkinter graphical interface
└── test_logic.py     # Automated tests (pytest)
```

---

## Installation

Python 3.8+ is required. No third-party packages are needed for the core logic or CLI.

The GUI interface uses **tkinter**, which ships with the standard Python distribution on most systems. If it is missing (some minimal Linux installs), install it with:

```bash
# macOS (via Homebrew)
brew install python-tk

# Debian / Ubuntu
sudo apt-get install python3-tk
```

To run the tests you need **pytest**:

```bash
pip install pytest
```

---

## Usage

Run every command from the `Day3/` directory.

### 1. Interactive prompt (`ui_input.py`)

Prompts you to type each value one at a time.

```bash
python ui_input.py
```

Example session:
```
Enter stock concentration (C1): 100
Enter desired concentration (C2): 10
Enter final volume (V2, in ul): 50

Stock to take:  5.00 ul
Diluent to add: 45.00 ul
Total volume:   50.00 ul
```

---

### 2. Command-line arguments (`ui_cli.py`)

Pass all three values as positional arguments — great for scripting.

```bash
python ui_cli.py <C1> <C2> <V2>
```

Example:
```bash
python ui_cli.py 100 10 50
```

Output:
```
Stock to take:  5.00 ul
Diluent to add: 45.00 ul
Total volume:   50.00 ul
```

If the wrong number of arguments is given the script prints usage instructions and exits with code 1.

---

### 3. Graphical interface (`ui_gui.py`)

Opens a small desktop window with labeled entry fields and a Calculate button.

```bash
python ui_gui.py
```

Fill in C1, C2, and V2, then click **Calculate**. The result appears below the button.

---

## Running the Tests

From the `Day3/` directory:

```bash
pytest test_logic.py -v
```

Expected output:
```
test_logic.py::test_standard_10x_dilution           PASSED
test_logic.py::test_standard_10x_large_volume       PASSED
test_logic.py::test_2x_dilution                     PASSED
test_logic.py::test_total_volume_always_equals_v2   PASSED
test_logic.py::test_no_dilution_needed_same_concentration PASSED
test_logic.py::test_desired_concentration_is_zero   PASSED
test_logic.py::test_zero_stock_concentration_raises PASSED
test_logic.py::test_very_large_dilution_factor      PASSED

8 passed in 0.XX s
```

---

## AI Collaboration

### Prompts used in this session

| Step | Prompt |
|------|--------|
| Initial script | *"Write a linear Python script for a biochemistry lab to calculate dilutions using C1V1=C2V2, forcing all inputs to be in ng/µl and µl, and outputting a simple 3-line protocol (Stock, Diluent, Total) using f-strings rounded to 2 decimal places."* |
| Refactor to module | *"Refactor the script so the calculation lives in a pure function `calculate_dilution(c1, c2, v2)` in `logic.py`, then create three separate UI files: `ui_input.py` (interactive prompts), `ui_cli.py` (sys.argv arguments), and `ui_gui.py` (tkinter window)."* |
| Add tests & docs | *"Add automated tests using pytest with at least 3–4 known-truth cases and at least one edge case. Also create a comprehensive README and a .gitignore."* |

### How AI helped

- **Separation of concerns** — AI suggested extracting the pure math into `logic.py` so all three UIs could import the same function without duplicating logic.
- **Edge-case identification** — AI identified the physically impossible case (`C1 = 0`) and added a test that asserts `ZeroDivisionError` is raised, rather than silently returning garbage.
- **pytest idioms** — AI used `pytest.approx` for all floating-point comparisons instead of `==`, avoiding brittle tests caused by floating-point rounding.
- **Documentation structure** — AI generated this README, including the formula table, usage examples with expected output, and the AI-collaboration section itself.
