"""Small validation primitives used by all scientific modules."""

from __future__ import annotations

import numpy as np

from qhe.exceptions import ValidationError


def hermiticity_residual(matrix: np.ndarray) -> float:
    """Return ``max(abs(H - H^dagger))`` after validating that the input is square."""

    array = np.asarray(matrix)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValidationError('Hermiticity requires a square rank-2 matrix.')
    return float(np.max(np.abs(array - array.conj().T)))


def assert_hermitian(matrix: np.ndarray, *, atol: float = 1e-12) -> None:
    """Raise when ``matrix`` is not Hermitian within an absolute tolerance."""

    residual = hermiticity_residual(matrix)
    if residual > atol:
        raise ValidationError(
            f'Matrix is not Hermitian within atol={atol:g}; max residual={residual:.3e}.'
        )
