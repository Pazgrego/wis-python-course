"""
logic.py - Core mathematical logic for Protein Thermal Shift Assay Analysis.

Provides functions to compute the first derivative of a fluorescence melting
curve and identify the melting temperature (Tm) at the peak of that derivative.
"""

import numpy as np
from typing import Tuple


def compute_first_derivative(
    temperature: np.ndarray,
    fluorescence: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the first derivative of the fluorescence signal with respect to
    temperature using numpy's gradient (central differences).

    Parameters
    ----------
    temperature : np.ndarray
        1-D array of temperature values (°C), must be monotonically increasing.
    fluorescence : np.ndarray
        1-D array of fluorescence intensity values, same length as temperature.

    Returns
    -------
    deriv_temp : np.ndarray
        Temperature array corresponding to the derivative values.
        Identical to the input temperature array (gradient preserves length).
    derivative : np.ndarray
        dF/dT values at each temperature point.

    Raises
    ------
    ValueError
        If temperature and fluorescence arrays have different lengths or
        fewer than 3 data points.
    """
    if len(temperature) != len(fluorescence):
        raise ValueError(
            f"temperature and fluorescence must have the same length, "
            f"got {len(temperature)} and {len(fluorescence)}."
        )
    if len(temperature) < 3:
        raise ValueError(
            "At least 3 data points are required to compute a meaningful derivative."
        )

    temperature = np.asarray(temperature, dtype=float)
    fluorescence = np.asarray(fluorescence, dtype=float)

    # numpy.gradient uses central differences for interior points and
    # forward/backward differences at the boundaries.
    derivative = np.gradient(fluorescence, temperature)

    return temperature, derivative


def find_tm(
    temperature: np.ndarray,
    fluorescence: np.ndarray,
) -> float:
    """
    Identify the melting temperature (Tm) as the temperature at which the
    first derivative of the fluorescence signal reaches its maximum value.

    In a thermal shift assay the fluorescence rises steeply as the protein
    unfolds and dye binds to exposed hydrophobic regions. The inflection point
    of this sigmoid — i.e. the peak of dF/dT — corresponds to the Tm.

    Parameters
    ----------
    temperature : np.ndarray
        1-D array of temperature values (°C).
    fluorescence : np.ndarray
        1-D array of fluorescence intensity values.

    Returns
    -------
    tm : float
        The melting temperature in °C.
    """
    temp_arr, derivative = compute_first_derivative(temperature, fluorescence)
    peak_index = int(np.argmax(derivative))
    tm = float(temp_arr[peak_index])
    return tm


def smooth_signal(
    fluorescence: np.ndarray,
    window: int = 3,
) -> np.ndarray:
    """
    Apply a simple moving-average smoother to reduce noise before
    differentiation.

    Parameters
    ----------
    fluorescence : np.ndarray
        Raw fluorescence signal.
    window : int
        Number of points in the moving-average window (must be odd and >= 3).

    Returns
    -------
    np.ndarray
        Smoothed fluorescence array (same length as input; edges use
        'reflect' padding).
    """
    if window < 3 or window % 2 == 0:
        raise ValueError("window must be an odd integer >= 3.")
    kernel = np.ones(window) / window
    smoothed = np.convolve(
        np.pad(fluorescence, window // 2, mode="reflect"),
        kernel,
        mode="valid",
    )
    return smoothed[: len(fluorescence)]
