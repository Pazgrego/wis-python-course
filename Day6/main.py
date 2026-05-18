"""
main.py
-------
Entry point for the Protein Sequence Analysis Tool.

Usage:
    python main.py

The program prompts for a UniProt accession ID, fetches the protein data,
runs biochemical analysis, and prints a formatted report.
"""

from uniprot_client import fetch_protein
from analyzer import analyze, PROPERTY_ORDER

# ── Visual helpers ─────────────────────────────────────────────────────────────

DIVIDER        = "═" * 62
SECTION_DIV    = "─" * 62
BAR_WIDTH      = 30          # characters for the ASCII bar chart


def _bar(pct: float, width: int = BAR_WIDTH) -> str:
    """Render a simple ASCII progress bar for a percentage value."""
    filled = round((pct / 100) * width)
    return f"[{'█' * filled}{'░' * (width - filled)}]"


# ── Report renderer ────────────────────────────────────────────────────────────

def print_report(protein_id: str, result: dict) -> None:
    seq_preview = result["sequence"][:60] + (
        "…" if len(result["sequence"]) > 60 else ""
    )

    print(f"\n{DIVIDER}")
    print(f"  🔬  PROTEIN SEQUENCE ANALYSIS REPORT")
    print(DIVIDER)
    print(f"  Accession ID  : {protein_id.upper()}")
    print(f"  Protein Name  : {result['name']}")
    print(f"  Gene          : {result['gene']}")
    print(f"  Organism      : {result['organism']}")
    print(f"  Sequence Len  : {result['length']} amino acids")
    print(f"  Sequence      : {seq_preview}")

    # ── Top-10 amino acids by frequency ───────────────────────────────────────
    print(f"\n{SECTION_DIV}")
    print("  TOP 10 AMINO ACID FREQUENCIES")
    print(SECTION_DIV)
    print(f"  {'AA':<4} {'Count':>6}   {'%':>6}   Chart")
    print(f"  {'──':<4} {'─────':>6}   {'─────':>6}   {'─' * BAR_WIDTH}")

    seq = result["sequence"]
    top10 = list(result["frequencies"].items())[:10]
    for aa, pct in top10:
        count = seq.count(aa)
        bar   = _bar(pct)
        print(f"  {aa:<4} {count:>6}   {pct:>5.2f}%  {bar}")

    # ── Biochemical property groups ────────────────────────────────────────────
    print(f"\n{SECTION_DIV}")
    print("  BIOCHEMICAL PROPERTY GROUPS")
    print(SECTION_DIV)

    order = PROPERTY_ORDER + [
        k for k in result["groups"] if k not in PROPERTY_ORDER
    ]

    for prop in order:
        if prop not in result["groups"]:
            continue
        grp = result["groups"][prop]
        total = grp["total_pct"]
        residues_str = "  ".join(
            f"{aa}={pct:.1f}%" for aa, pct in sorted(grp["residues"].items())
        )
        bar = _bar(total)
        print(f"\n  ▸ {prop}  ({total:.1f}%)")
        print(f"    {bar}")
        print(f"    Residues: {residues_str}")

    print(f"\n{DIVIDER}\n")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║        UniProt Protein Sequence Analysis Tool           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("\n  Examples: P69905 (Hemoglobin α), P01308 (Insulin),")
    print("            P00533 (EGFR), P04637 (p53), P0DTD1 (SARS-CoV-2)\n")

    protein_id = input("  Enter a UniProt Accession ID: ").strip()

    if not protein_id:
        print("  ✗  No ID entered. Exiting.")
        return

    print(f"\n  ⟳  Fetching '{protein_id.upper()}' from UniProt …")

    try:
        raw_data = fetch_protein(protein_id)
    except (ValueError, ConnectionError) as exc:
        print(f"\n  ✗  Error: {exc}\n")
        return

    print("  ✓  Data received. Running analysis …\n")

    try:
        result = analyze(raw_data)
    except KeyError as exc:
        print(f"\n  ✗  Analysis error: {exc}\n")
        return

    print_report(protein_id, result)


if __name__ == "__main__":
    main()
