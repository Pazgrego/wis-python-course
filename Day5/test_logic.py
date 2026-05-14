"""
test_logic.py - Unit tests for the core Tm-finding logic.

Uses synthetic sigmoidal (Boltzmann) curves with known inflection points so
every assertion has a ground-truth reference.  Run with:

    python -m pytest test_logic.py -v
"""

import numpy as np
import pytest
from logic import compute_first_derivative, find_tm, smooth_signal


# ── Helpers ───────────────────────────────────────────────────────────────────

def boltzmann_sigmoid(temp: np.ndarray, tm: float, slope: float = 1.0) -> np.ndarray:
    """
    Generate a Boltzmann sigmoidal fluorescence curve.

    F(T) = F_max / (1 + exp(-(T - Tm) / slope))

    The inflection point — and therefore the peak of dF/dT — is at T = Tm.
    """
    return 1.0 / (1.0 + np.exp(-(temp - tm) / slope))


# ── Tests: compute_first_derivative ──────────────────────────────────────────

class TestComputeFirstDerivative:

    def test_output_shapes_match_input(self):
        temp = np.linspace(35, 75, 41)
        fluor = boltzmann_sigmoid(temp, tm=50.0)
        deriv_temp, deriv = compute_first_derivative(temp, fluor)
        assert deriv_temp.shape == temp.shape
        assert deriv.shape == temp.shape

    def test_derivative_of_constant_is_zero(self):
        temp = np.linspace(35, 75, 41)
        fluor = np.ones_like(temp) * 300.0
        _, deriv = compute_first_derivative(temp, fluor)
        np.testing.assert_allclose(deriv, 0.0, atol=1e-10)

    def test_derivative_of_linear_is_constant(self):
        temp = np.linspace(35, 75, 41)
        slope = 5.0
        fluor = slope * temp + 10.0
        _, deriv = compute_first_derivative(temp, fluor)
        # Central-difference gradient of a linear function is exact
        np.testing.assert_allclose(deriv, slope, atol=1e-8)

    def test_raises_on_length_mismatch(self):
        with pytest.raises(ValueError, match="same length"):
            compute_first_derivative(
                np.arange(10, dtype=float),
                np.arange(8, dtype=float),
            )

    def test_raises_on_too_few_points(self):
        with pytest.raises(ValueError, match="3 data points"):
            compute_first_derivative(
                np.array([40.0, 45.0]),
                np.array([100.0, 200.0]),
            )

    def test_derivative_peaks_at_inflection(self):
        """Peak of dF/dT must occur at or very near the sigmoid's Tm."""
        temp = np.linspace(30, 70, 401)   # high-resolution grid
        tm_true = 52.0
        fluor = boltzmann_sigmoid(temp, tm=tm_true, slope=2.0)
        _, deriv = compute_first_derivative(temp, fluor)
        peak_temp = temp[np.argmax(deriv)]
        assert abs(peak_temp - tm_true) < 0.5, (
            f"Derivative peak at {peak_temp:.2f} °C, expected ~{tm_true} °C"
        )


# ── Tests: find_tm ────────────────────────────────────────────────────────────

class TestFindTm:

    def test_tm_known_inflection_coarse_grid(self):
        """find_tm must return the inflection point ±1 °C on a 1 °C grid."""
        temp = np.arange(35, 76, dtype=float)   # 1 °C steps
        tm_true = 50.0
        fluor = boltzmann_sigmoid(temp, tm=tm_true, slope=2.0) * 500
        tm_calc = find_tm(temp, fluor)
        assert abs(tm_calc - tm_true) <= 1.0, (
            f"Tm = {tm_calc} °C, expected {tm_true} ± 1 °C"
        )

    def test_tm_known_inflection_fine_grid(self):
        """find_tm on a 0.1 °C grid must be within 0.5 °C of truth."""
        temp = np.arange(35, 75.1, 0.1)
        tm_true = 47.5
        fluor = boltzmann_sigmoid(temp, tm=tm_true, slope=1.5) * 400
        tm_calc = find_tm(temp, fluor)
        assert abs(tm_calc - tm_true) <= 0.5, (
            f"Tm = {tm_calc} °C, expected {tm_true} ± 0.5 °C"
        )

    def test_tm_returns_float(self):
        temp = np.linspace(35, 75, 41)
        fluor = boltzmann_sigmoid(temp, tm=55.0)
        assert isinstance(find_tm(temp, fluor), float)

    def test_tm_with_noise(self):
        """Tm should still be within 2 °C of truth under moderate noise."""
        rng = np.random.default_rng(42)
        temp = np.linspace(35, 75, 81)
        tm_true = 53.0
        fluor = boltzmann_sigmoid(temp, tm=tm_true, slope=2.0) * 500
        noisy = fluor + rng.normal(0, 5, size=len(temp))
        tm_calc = find_tm(temp, noisy)
        assert abs(tm_calc - tm_true) <= 2.0, (
            f"Noisy Tm = {tm_calc} °C, expected {tm_true} ± 2 °C"
        )

    def test_higher_tm_with_ligand(self):
        """Ligand should produce a higher Tm than protein alone."""
        temp = np.arange(35, 76, dtype=float)
        tm_protein = 47.0
        tm_ligand  = 54.0
        f_protein = boltzmann_sigmoid(temp, tm=tm_protein, slope=2.0) * 400
        f_ligand  = boltzmann_sigmoid(temp, tm=tm_ligand,  slope=2.0) * 400

        calc_p = find_tm(temp, f_protein)
        calc_l = find_tm(temp, f_ligand)
        assert calc_l > calc_p, (
            f"Expected Tm(+ligand)={calc_l} > Tm(−ligand)={calc_p}"
        )

    def test_delta_tm_sign_indicates_stabilisation(self):
        """ΔTm = Tm(+ligand) − Tm(−ligand) should be positive."""
        temp = np.arange(35, 76, dtype=float)
        f_p = boltzmann_sigmoid(temp, tm=47.0, slope=2.0)
        f_l = boltzmann_sigmoid(temp, tm=54.0, slope=2.0)
        delta = find_tm(temp, f_l) - find_tm(temp, f_p)
        assert delta > 0, f"ΔTm = {delta:.2f}, expected positive"


# ── Tests: smooth_signal ─────────────────────────────────────────────────────

class TestSmoothSignal:

    def test_smoothed_length_unchanged(self):
        signal = np.random.rand(41)
        smoothed = smooth_signal(signal, window=5)
        assert len(smoothed) == len(signal)

    def test_constant_signal_unchanged(self):
        signal = np.ones(41) * 250.0
        smoothed = smooth_signal(signal, window=5)
        np.testing.assert_allclose(smoothed, 250.0, atol=1e-10)

    def test_raises_on_even_window(self):
        with pytest.raises(ValueError, match="odd integer"):
            smooth_signal(np.ones(20), window=4)

    def test_raises_on_window_less_than_3(self):
        with pytest.raises(ValueError, match="odd integer"):
            smooth_signal(np.ones(20), window=1)

    def test_smoothing_reduces_noise(self):
        rng = np.random.default_rng(0)
        base = boltzmann_sigmoid(np.linspace(35, 75, 81), tm=52.0)
        noisy = base + rng.normal(0, 0.05, size=81)
        smoothed = smooth_signal(noisy, window=7)
        # Smoothed signal should have smaller standard deviation from baseline
        assert np.std(smoothed - base) < np.std(noisy - base)
