"""Massive two-band Dirac warm-up Hamiltonian.

This module is intentionally small.  Its role is to provide a convention-consistent
starting point for the Stage-2 Berry-curvature validation notebook, not to replace the
lattice Harper-Hofstadter model as the central topological example.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qhe.validation import assert_hermitian


@dataclass(frozen=True, slots=True)
class DiracParameters:
    """Parameters of ``H_D = v_F (kx sigma_x + ky sigma_y) + Delta sigma_z``."""

    v_fermi: float = 1.0
    mass: float = 0.25

    def __post_init__(self) -> None:
        if self.v_fermi <= 0.0:
            raise ValueError('v_fermi must be strictly positive.')


def massive_dirac_hamiltonian(
    kx: float,
    ky: float,
    parameters: DiracParameters | None = None,
) -> np.ndarray:
    """Return the convention-consistent 2D massive Dirac Hamiltonian.

    The Pauli-matrix convention is standard: ``sigma_y[[0, 1], [1, 0]]`` is replaced by
    ``[[0, -i], [i, 0]]``.  The returned matrix is checked for Hermiticity before return.
    """

    params = parameters or DiracParameters()
    off_diagonal = params.v_fermi * complex(kx, -ky)
    matrix = np.array(
        [[params.mass, off_diagonal], [np.conjugate(off_diagonal), -params.mass]],
        dtype=np.complex128,
    )
    assert_hermitian(matrix)
    return matrix


def massive_dirac_energies(
    kx: float,
    ky: float,
    parameters: DiracParameters | None = None,
) -> tuple[float, float]:
    """Return analytic lower and upper energies ``E_-`` and ``E_+``."""

    params = parameters or DiracParameters()
    amplitude = float(
        np.sqrt(params.v_fermi**2 * (float(kx) ** 2 + float(ky) ** 2) + params.mass**2)
    )
    return -amplitude, amplitude


__all__ = ['DiracParameters', 'massive_dirac_energies', 'massive_dirac_hamiltonian']
