"""Small validation primitives available from Stage 0 onward."""

from __future__ import annotations

import numpy as np

from qhe.exceptions import ValidationError


def assert_hermitian(matrix: np.ndarray, *, atol: float = 1e-12) -> None:
    """Raise when ``matrix`` is not Hermitian within an absolute tolerance.

    This compact helper exists already in Stage 0 because Stage 1 must validate every
    real-space and Bloch Hamiltonian immediately after construction.
    """

    array = np.asarray(matrix)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValidationError("Hermiticity requires a square rank-2 matrix.")
    if not np.allclose(array, array.conj().T, atol=atol, rtol=0.0):
        max_residual = float(np.max(np.abs(array - array.conj().T)))
        raise ValidationError(
            f"Matrix is not Hermitian within atol={atol:g}; max residual={max_residual:.3e}."
        )
