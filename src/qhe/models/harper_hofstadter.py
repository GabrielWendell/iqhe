r"""Canonical Harper-Hofstadter Hamiltonians under frozen Stage-1 conventions.

Parent real-space model
-----------------------
In Landau gauge :math:`A=(0,Bx,0)`, with a positive elementary charge ``e`` and electron
charge ``-e``, the Peierls-substituted square-lattice Hamiltonian is

.. math::

   H = -t_x \sum_{m,n} (c^\dagger_{m+1,n}c_{m,n} + h.c.)
       -t_y \sum_{m,n} (e^{i 2\pi \phi m} c^\dagger_{m,n+1}c_{m,n} + h.c.).

Here :math:`\phi=p/q=\Phi/\Phi_0`, with coprime integers ``p`` and ``q``.  Every
Hamiltonian in this module is derived from this parent definition; only the boundary
conditions and Fourier transforms change.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd

import numpy as np

from qhe.validation import assert_hermitian


@dataclass(frozen=True, slots=True)
class HarperHofstadterParameters:
    """Physical parameters shared by all Harper-Hofstadter geometries."""

    p: int = 1
    q: int = 3
    tx: float = 1.0
    ty: float = 1.0
    lattice_spacing: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.p, int) or not isinstance(self.q, int):
            raise TypeError('p and q must be integers.')
        if self.q <= 0:
            raise ValueError('q must be a positive integer.')
        if gcd(self.p, self.q) != 1:
            raise ValueError('p and q must be coprime.')
        if self.tx <= 0.0 or self.ty <= 0.0:
            raise ValueError('tx and ty must be strictly positive.')
        if self.lattice_spacing <= 0.0:
            raise ValueError('lattice_spacing must be strictly positive.')

    @property
    def flux(self) -> float:
        """Magnetic flux per plaquette in flux-quantum units."""

        return self.p / self.q

    @property
    def magnetic_period(self) -> int:
        """Number of sites in the Landau-gauge magnetic unit cell along x."""

        return self.q


@dataclass(frozen=True, slots=True)
class MagneticBrillouinZone:
    """Closed-open momentum-domain bounds for the magnetic Brillouin zone."""

    kx_min: float
    kx_max: float
    ky_min: float
    ky_max: float

    @property
    def kx_width(self) -> float:
        return self.kx_max - self.kx_min

    @property
    def ky_width(self) -> float:
        return self.ky_max - self.ky_min


def magnetic_brillouin_zone(
    parameters: HarperHofstadterParameters | None = None,
) -> MagneticBrillouinZone:
    """Return ``[-pi/(qa), pi/(qa)) x [-pi/a, pi/a)`` for the chosen flux."""

    params = parameters or HarperHofstadterParameters()
    a = params.lattice_spacing
    return MagneticBrillouinZone(
        kx_min=-np.pi / (params.q * a),
        kx_max=np.pi / (params.q * a),
        ky_min=-np.pi / a,
        ky_max=np.pi / a,
    )


def peierls_phase(
    m: int,
    parameters: HarperHofstadterParameters | None = None,
) -> complex:
    """Return the forward-y hopping phase ``exp(+i 2 pi phi m)``."""

    params = parameters or HarperHofstadterParameters()
    return complex(np.exp(2.0j * np.pi * params.flux * int(m)))


def site_index(m: int, n: int, ly: int) -> int:
    """Map lattice coordinates to the frozen row-major state-vector convention.

    ``m`` labels the x coordinate, ``n`` labels the y coordinate, and reshaping a state
    vector yields an array of shape ``(Lx, Ly)``.  This convention intentionally supports
    rectangular systems and replaces the legacy square-root inference of lattice sizes.
    """

    if ly <= 0:
        raise ValueError('ly must be strictly positive.')
    if m < 0 or n < 0 or n >= ly:
        raise IndexError('Invalid lattice coordinate for the supplied ly.')
    return int(m) * int(ly) + int(n)


def site_coordinates(index: int, ly: int) -> tuple[int, int]:
    """Invert :func:`site_index` for a state-vector index."""

    if ly <= 0:
        raise ValueError('ly must be strictly positive.')
    if index < 0:
        raise IndexError('index must be non-negative.')
    return divmod(int(index), int(ly))


def open_hamiltonian(
    lx: int,
    ly: int,
    parameters: HarperHofstadterParameters | None = None,
) -> np.ndarray:
    """Build the parent Harper-Hofstadter Hamiltonian with open x and y boundaries."""

    if lx <= 0 or ly <= 0:
        raise ValueError('lx and ly must be strictly positive.')
    params = parameters or HarperHofstadterParameters()
    matrix = np.zeros((lx * ly, lx * ly), dtype=np.complex128)

    for m in range(lx):
        for n in range(ly):
            origin = site_index(m, n, ly)
            if m + 1 < lx:
                right = site_index(m + 1, n, ly)
                matrix[right, origin] += -params.tx
                matrix[origin, right] += -params.tx
            if n + 1 < ly:
                up = site_index(m, n + 1, ly)
                phase = peierls_phase(m, params)
                matrix[up, origin] += -params.ty * phase
                matrix[origin, up] += -params.ty * np.conjugate(phase)

    assert_hermitian(matrix)
    return matrix


def ribbon_hamiltonian(
    lx: int,
    ky: float,
    parameters: HarperHofstadterParameters | None = None,
) -> np.ndarray:
    """Build the x-open/y-periodic Harper-Hofstadter ribbon Hamiltonian.

    The Fourier convention is ``c_(m,n) = sum_ky exp(+i ky a n)c_m(ky)/sqrt(Ly)``.  It
    leads to an onsite term ``-2 ty cos(ky a - 2 pi phi m)`` and keeps the parent Peierls
    phase explicit.
    """

    if lx <= 0:
        raise ValueError('lx must be strictly positive.')
    params = parameters or HarperHofstadterParameters()
    sites = np.arange(lx, dtype=float)
    matrix = np.diag(
        -2.0
        * params.ty
        * np.cos(float(ky) * params.lattice_spacing - 2.0 * np.pi * params.flux * sites)
    ).astype(np.complex128)

    for m in range(lx - 1):
        matrix[m + 1, m] += -params.tx
        matrix[m, m + 1] += -params.tx

    assert_hermitian(matrix)
    return matrix


def bloch_hamiltonian(
    kx: float,
    ky: float,
    parameters: HarperHofstadterParameters | None = None,
) -> np.ndarray:
    """Build the q-by-q Harper-Hofstadter magnetic Bloch Hamiltonian.

    The magnetic-cell convention is ``psi_(R,r) = exp(+i q a kx R) u_r(k)`` for
    ``r=0,...,q-1``.  The resulting reduced Brillouin zone is provided by
    :func:`magnetic_brillouin_zone`.
    """

    params = parameters or HarperHofstadterParameters()
    a = params.lattice_spacing
    q = params.q

    if q == 1:
        matrix = np.array(
            [[-2.0 * params.tx * np.cos(a * float(kx)) - 2.0 * params.ty * np.cos(a * float(ky))]],
            dtype=np.complex128,
        )
        assert_hermitian(matrix)
        return matrix

    r = np.arange(q, dtype=float)
    diagonal = -2.0 * params.ty * np.cos(a * float(ky) - 2.0 * np.pi * params.flux * r)
    matrix = np.diag(diagonal).astype(np.complex128)

    for sublattice in range(q - 1):
        matrix[sublattice + 1, sublattice] += -params.tx
        matrix[sublattice, sublattice + 1] += -params.tx

    boundary_phase = np.exp(1.0j * q * a * float(kx))
    matrix[0, q - 1] += -params.tx * np.conjugate(boundary_phase)
    matrix[q - 1, 0] += -params.tx * boundary_phase

    assert_hermitian(matrix)
    return matrix


def bloch_hamiltonian_derivatives(
    kx: float,
    ky: float,
    parameters: HarperHofstadterParameters | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return analytic ``(dH/dkx, dH/dky)`` for future Kubo-curvature calculations."""

    params = parameters or HarperHofstadterParameters()
    a = params.lattice_spacing
    q = params.q

    if q == 1:
        d_kx = np.array([[2.0 * params.tx * a * np.sin(a * float(kx))]], dtype=np.complex128)
        d_ky = np.array([[2.0 * params.ty * a * np.sin(a * float(ky))]], dtype=np.complex128)
        assert_hermitian(d_kx)
        assert_hermitian(d_ky)
        return d_kx, d_ky

    r = np.arange(q, dtype=float)
    d_kx = np.zeros((q, q), dtype=np.complex128)
    d_ky = np.diag(
        2.0 * params.ty * a * np.sin(a * float(ky) - 2.0 * np.pi * params.flux * r)
    ).astype(np.complex128)

    boundary_phase = np.exp(1.0j * q * a * float(kx))
    prefactor = q * a * params.tx
    d_kx[0, q - 1] += 1.0j * prefactor * np.conjugate(boundary_phase)
    d_kx[q - 1, 0] += -1.0j * prefactor * boundary_phase

    assert_hermitian(d_kx)
    assert_hermitian(d_ky)
    return d_kx, d_ky


__all__ = [
    'HarperHofstadterParameters',
    'MagneticBrillouinZone',
    'bloch_hamiltonian',
    'bloch_hamiltonian_derivatives',
    'magnetic_brillouin_zone',
    'open_hamiltonian',
    'peierls_phase',
    'ribbon_hamiltonian',
    'site_coordinates',
    'site_index',
]
