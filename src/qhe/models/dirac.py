"""Massive two-band Dirac warm-up Hamiltonian.

The continuum Dirac model is used in Stage 2 only as a local Berry-curvature validation target.
Its half-integer continuum contribution is not treated as a lattice-band Chern number because the
momentum plane is noncompact.
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
            raise ValueError("v_fermi must be strictly positive.")
        if self.mass == 0.0:
            raise ValueError("mass must be non-zero for the gapped Stage-2 Dirac warm-up.")


def massive_dirac_hamiltonian(
    kx: float,
    ky: float,
    parameters: DiracParameters | None = None,
) -> np.ndarray:
    """Return the convention-consistent 2D massive Dirac Hamiltonian."""

    params = parameters or DiracParameters()
    off_diagonal = params.v_fermi * complex(kx, -ky)
    matrix = np.array(
        [[params.mass, off_diagonal], [np.conjugate(off_diagonal), -params.mass]],
        dtype=np.complex128,
    )
    assert_hermitian(matrix)
    return matrix


def massive_dirac_hamiltonian_derivatives(
    parameters: DiracParameters | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return exact ``(dH/dkx, dH/dky)`` for the massive Dirac Hamiltonian."""

    params = parameters or DiracParameters()
    derivative_x = params.v_fermi * np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
    derivative_y = params.v_fermi * np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
    assert_hermitian(derivative_x)
    assert_hermitian(derivative_y)
    return derivative_x, derivative_y


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


def massive_dirac_berry_curvature(
    kx: float,
    ky: float,
    parameters: DiracParameters | None = None,
) -> tuple[float, float]:
    r"""Return analytic ``(Omega_-, Omega_+)`` under the frozen Berry convention.

    For ``H_D=v_F(kx sigma_x+ky sigma_y)+Delta sigma_z`` this is

    .. math::

       \Omega_\pm(k)=\mp\frac{\Delta v_F^2}
       {2(v_F^2|k|^2+\Delta^2)^{3/2}}.
    """

    params = parameters or DiracParameters()
    denominator = (
        params.v_fermi**2 * (float(kx) ** 2 + float(ky) ** 2) + params.mass**2
    ) ** 1.5
    lower = params.mass * params.v_fermi**2 / (2.0 * denominator)
    return float(lower), float(-lower)


__all__ = [
    "DiracParameters",
    "massive_dirac_berry_curvature",
    "massive_dirac_energies",
    "massive_dirac_hamiltonian",
    "massive_dirac_hamiltonian_derivatives",
]
