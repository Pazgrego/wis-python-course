# Day 06 — Protein Sequence Analysis

Fetches a protein from [UniProt](https://www.uniprot.org/) by accession ID, analyzes its amino acid sequence, and prints a report in the terminal (frequencies + biochemical groups).

---

## How to run (step by step)

Do these from a terminal, **in order**.

### Step 1 — Open the project folder

```bash
cd Day6
```

Stay in this folder for the steps below.

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the tool

```bash
python main.py
```

When prompted, enter a UniProt accession ID (examples below). You need **internet** — data is loaded from the UniProt API.

### Step 4 — Run tests (optional)

```bash
python -m pytest test_analyzer.py -v
```

Tests use mock data only — **no internet** required.

---

## Example accession IDs

| ID | Protein |
|----|---------|
| `P69905` | Hemoglobin α |
| `P01308` | Insulin |
| `P00533` | EGFR |
| `P04637` | p53 |
| `P0DTD1` | SARS-CoV-2 replicase |

---

## Project files

```
Day6/
├── main.py             # Run this — prompts for ID, prints report
├── uniprot_client.py   # Fetches JSON from UniProt
├── analyzer.py         # Sequence analysis logic
├── test_analyzer.py    # Unit tests
└── requirements.txt
```

---

## Quick reference

| Goal | Command |
|------|---------|
| Analyze a protein | `python main.py` |
| Run tests | `python -m pytest test_analyzer.py -v` |

**Modules:** `uniprot_client.py` handles the network; `analyzer.py` handles the math; `main.py` ties them together and prints the output.
