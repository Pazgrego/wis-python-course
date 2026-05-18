"""
test_analyzer.py
----------------
Unit tests for analyzer.py.

All tests use a mock UniProt JSON response — no live network calls are made.
Run with:  pytest test_analyzer.py -v
"""

import pytest
from analyzer import (
    extract_protein_name,
    extract_organism,
    extract_sequence,
    extract_sequence_length,
    extract_gene_name,
    calculate_aa_frequencies,
    group_by_properties,
    analyze,
)

# ── Shared mock data ───────────────────────────────────────────────────────────

MOCK_JSON = {
    "proteinDescription": {
        "recommendedName": {
            "fullName": {"value": "Hemoglobin subunit alpha"}
        }
    },
    "organism": {"scientificName": "Homo sapiens"},
    "genes": [{"geneName": {"value": "HBA1"}}],
    "sequence": {
        "value": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHG",
        "length": 60,
    },
}

# A minimal sequence used to verify exact numeric results
SIMPLE_SEQ = "AAAVVV"   # A×3 (50%), V×3 (50%)


# ── Metadata extraction tests ──────────────────────────────────────────────────

class TestExtractors:

    def test_protein_name_recommended(self):
        assert extract_protein_name(MOCK_JSON) == "Hemoglobin subunit alpha"

    def test_protein_name_fallback_submission(self):
        data = {
            "proteinDescription": {
                "submissionNames": [{"fullName": {"value": "Hypothetical protein"}}]
            }
        }
        assert extract_protein_name(data) == "Hypothetical protein"

    def test_protein_name_unknown(self):
        assert extract_protein_name({}) == "Unknown protein"

    def test_organism(self):
        assert extract_organism(MOCK_JSON) == "Homo sapiens"

    def test_organism_unknown(self):
        assert extract_organism({}) == "Unknown organism"

    def test_sequence(self):
        seq = extract_sequence(MOCK_JSON)
        assert seq.startswith("MVLSPADKTNVK")
        assert seq == seq.upper()   # must be uppercase

    def test_sequence_missing_raises(self):
        with pytest.raises(KeyError):
            extract_sequence({})

    def test_sequence_length(self):
        assert extract_sequence_length(MOCK_JSON) == 60

    def test_gene_name(self):
        assert extract_gene_name(MOCK_JSON) == "HBA1"

    def test_gene_name_missing(self):
        assert extract_gene_name({}) == "N/A"


# ── Frequency calculation tests ────────────────────────────────────────────────

class TestFrequencies:

    def test_simple_50_50(self):
        freqs = calculate_aa_frequencies(SIMPLE_SEQ)
        assert freqs["A"] == pytest.approx(50.0)
        assert freqs["V"] == pytest.approx(50.0)

    def test_percentages_sum_to_100(self):
        seq = extract_sequence(MOCK_JSON)
        freqs = calculate_aa_frequencies(seq)
        total = sum(freqs.values())
        assert total == pytest.approx(100.0, abs=0.1)

    def test_empty_sequence(self):
        assert calculate_aa_frequencies("") == {}

    def test_sorted_descending(self):
        freqs = calculate_aa_frequencies("AAABBC")
        values = list(freqs.values())
        assert values == sorted(values, reverse=True)

    def test_single_aa(self):
        freqs = calculate_aa_frequencies("GGGG")
        assert freqs == {"G": 100.0}

    def test_two_digit_precision(self):
        # 1 residue in 3 → 33.33 %
        freqs = calculate_aa_frequencies("AAK")
        assert freqs["K"] == pytest.approx(33.33, abs=0.01)


# ── Property grouping tests ────────────────────────────────────────────────────

class TestGrouping:

    def test_hydrophobic_group_present(self):
        freqs = calculate_aa_frequencies("AAAVVV")
        groups = group_by_properties(freqs)
        assert "Hydrophobic" in groups
        assert groups["Hydrophobic"]["total_pct"] == pytest.approx(100.0)

    def test_charged_groups(self):
        freqs = calculate_aa_frequencies("KKDDE")
        groups = group_by_properties(freqs)
        assert groups["Positively Charged"]["total_pct"] > 0
        assert groups["Negatively Charged"]["total_pct"] > 0

    def test_group_totals_sum_to_100(self):
        seq = extract_sequence(MOCK_JSON)
        freqs = calculate_aa_frequencies(seq)
        groups = group_by_properties(freqs)
        grand_total = sum(g["total_pct"] for g in groups.values())
        assert grand_total == pytest.approx(100.0, abs=0.5)

    def test_unknown_aa_captured(self):
        # 'X' is not a standard amino acid
        freqs = {"X": 100.0}
        groups = group_by_properties(freqs)
        assert "Unknown / Modified" in groups
        assert groups["Unknown / Modified"]["residues"]["X"] == 100.0


# ── Full pipeline test ─────────────────────────────────────────────────────────

class TestAnalyzePipeline:

    def test_analyze_returns_expected_keys(self):
        result = analyze(MOCK_JSON)
        for key in ("name", "organism", "gene", "length", "sequence",
                    "frequencies", "groups"):
            assert key in result, f"Missing key: {key}"

    def test_analyze_name(self):
        assert analyze(MOCK_JSON)["name"] == "Hemoglobin subunit alpha"

    def test_analyze_organism(self):
        assert analyze(MOCK_JSON)["organism"] == "Homo sapiens"

    def test_analyze_sequence_uppercase(self):
        result = analyze(MOCK_JSON)
        assert result["sequence"] == result["sequence"].upper()

    def test_analyze_frequencies_non_empty(self):
        result = analyze(MOCK_JSON)
        assert len(result["frequencies"]) > 0
