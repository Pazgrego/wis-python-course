"""
analyzer.py
-----------
Pure business logic: extracts protein metadata and performs
biochemical analysis on the amino acid sequence.
No network calls live here — only data transformation.
"""

from collections import Counter

# ── Amino acid classification ──────────────────────────────────────────────────
# Each single-letter code maps to a biochemical property group.
AA_PROPERTIES: dict[str, str] = {
    # Hydrophobic (nonpolar, aliphatic / aromatic)
    "A": "Hydrophobic", "V": "Hydrophobic", "I": "Hydrophobic",
    "L": "Hydrophobic", "M": "Hydrophobic", "F": "Hydrophobic",
    "W": "Hydrophobic", "P": "Hydrophobic",

    # Polar (uncharged)
    "G": "Polar", "S": "Polar", "T": "Polar", "C": "Polar",
    "Y": "Polar", "N": "Polar", "Q": "Polar",

    # Positively charged (basic)
    "K": "Positively Charged", "R": "Positively Charged", "H": "Positively Charged",

    # Negatively charged (acidic)
    "D": "Negatively Charged", "E": "Negatively Charged",
}

# Display order for the grouped summary
PROPERTY_ORDER = [
    "Hydrophobic",
    "Polar",
    "Positively Charged",
    "Negatively Charged",
]


# ── Metadata extraction ────────────────────────────────────────────────────────

def extract_protein_name(data: dict) -> str:
    """Return the recommended full protein name from UniProt JSON."""
    try:
        return (
            data["proteinDescription"]
            ["recommendedName"]
            ["fullName"]
            ["value"]
        )
    except (KeyError, TypeError):
        # Fall back to submitted name if recommended name is absent
        try:
            return (
                data["proteinDescription"]
                ["submissionNames"][0]
                ["fullName"]
                ["value"]
            )
        except (KeyError, TypeError, IndexError):
            return "Unknown protein"


def extract_organism(data: dict) -> str:
    """Return the scientific name of the source organism."""
    try:
        return data["organism"]["scientificName"]
    except (KeyError, TypeError):
        return "Unknown organism"


def extract_sequence(data: dict) -> str:
    """
    Extract the raw amino acid sequence string.

    Returns:
        Uppercase sequence string, e.g. 'MVLSPADKTNVK...'

    Raises:
        KeyError: If the sequence field is absent in the JSON.
    """
    try:
        return data["sequence"]["value"].upper()
    except (KeyError, TypeError) as exc:
        raise KeyError(
            "Could not find 'sequence.value' in the UniProt JSON response."
        ) from exc


def extract_sequence_length(data: dict) -> int:
    """Return the sequence length as reported by UniProt."""
    try:
        return data["sequence"]["length"]
    except (KeyError, TypeError):
        return 0


def extract_gene_name(data: dict) -> str:
    """Return the primary gene name, if available."""
    try:
        return data["genes"][0]["geneName"]["value"]
    except (KeyError, TypeError, IndexError):
        return "N/A"


# ── Sequence analysis ──────────────────────────────────────────────────────────

def calculate_aa_frequencies(sequence: str) -> dict[str, float]:
    """
    Calculate the percentage frequency of every amino acid in the sequence.

    Args:
        sequence: Uppercase single-letter amino acid string.

    Returns:
        Dict mapping each amino acid letter to its percentage (0–100),
        sorted from most to least frequent.
    """
    if not sequence:
        return {}

    total = len(sequence)
    counts = Counter(sequence)

    frequencies = {
        aa: round((count / total) * 100, 2)
        for aa, count in counts.items()
    }

    # Sort by frequency descending, then alphabetically as tiebreaker
    return dict(sorted(frequencies.items(), key=lambda x: (-x[1], x[0])))


def group_by_properties(frequencies: dict[str, float]) -> dict[str, dict]:
    """
    Group amino acid frequency data by biochemical property.

    Args:
        frequencies: Output of calculate_aa_frequencies().

    Returns:
        Dict with property names as keys. Each value is a sub-dict:
            {
                'residues': {'A': 8.5, 'V': 6.2, ...},
                'total_pct': 14.7
            }
    """
    groups: dict[str, dict] = {
        prop: {"residues": {}, "total_pct": 0.0}
        for prop in PROPERTY_ORDER
    }
    unknown_group: dict[str, float] = {}

    for aa, pct in frequencies.items():
        prop = AA_PROPERTIES.get(aa)
        if prop and prop in groups:
            groups[prop]["residues"][aa] = pct
            groups[prop]["total_pct"] = round(
                groups[prop]["total_pct"] + pct, 2
            )
        else:
            unknown_group[aa] = pct

    if unknown_group:
        groups["Unknown / Modified"] = {
            "residues": unknown_group,
            "total_pct": round(sum(unknown_group.values()), 2),
        }

    return groups


def analyze(data: dict) -> dict:
    """
    Top-level function: run the full analysis pipeline on raw UniProt JSON.

    Returns a structured result dict consumed by main.py for reporting.
    """
    sequence = extract_sequence(data)
    frequencies = calculate_aa_frequencies(sequence)
    groups = group_by_properties(frequencies)

    return {
        "name": extract_protein_name(data),
        "organism": extract_organism(data),
        "gene": extract_gene_name(data),
        "length": extract_sequence_length(data),
        "sequence": sequence,
        "frequencies": frequencies,
        "groups": groups,
    }
