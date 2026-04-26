import pytest
from logic import calculate_dilution


# --- happy-path tests ---

def test_standard_10x_dilution():
    """10x dilution: take 5 ul from 100 ug/ul stock into 50 ul final."""
    v1, diluent = calculate_dilution(c1=100, c2=10, v2=50)
    assert v1 == pytest.approx(5.0)
    assert diluent == pytest.approx(45.0)


def test_standard_10x_large_volume():
    """10x dilution at 200 ul final volume."""
    v1, diluent = calculate_dilution(c1=1000, c2=100, v2=200)
    assert v1 == pytest.approx(20.0)
    assert diluent == pytest.approx(180.0)


def test_2x_dilution():
    """2x dilution: half stock, half diluent."""
    v1, diluent = calculate_dilution(c1=50, c2=25, v2=100)
    assert v1 == pytest.approx(50.0)
    assert diluent == pytest.approx(50.0)


def test_total_volume_always_equals_v2():
    """v1 + diluent must always sum back to v2."""
    v1, diluent = calculate_dilution(c1=80, c2=20, v2=400)
    assert v1 + diluent == pytest.approx(400.0)


# --- edge-case tests ---

def test_no_dilution_needed_same_concentration():
    """When C1 == C2, the full volume is stock and diluent is 0."""
    v1, diluent = calculate_dilution(c1=10, c2=10, v2=100)
    assert v1 == pytest.approx(100.0)
    assert diluent == pytest.approx(0.0)


def test_desired_concentration_is_zero():
    """C2 = 0 means pure diluent — no stock needed."""
    v1, diluent = calculate_dilution(c1=100, c2=0, v2=50)
    assert v1 == pytest.approx(0.0)
    assert diluent == pytest.approx(50.0)


def test_zero_stock_concentration_raises():
    """C1 = 0 is physically impossible and must raise ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        calculate_dilution(c1=0, c2=10, v2=50)


def test_very_large_dilution_factor():
    """1,000,000x dilution — tiny stock volume, nearly all diluent."""
    v1, diluent = calculate_dilution(c1=1e6, c2=1, v2=1000)
    assert v1 == pytest.approx(0.001)
    assert diluent == pytest.approx(999.999)
