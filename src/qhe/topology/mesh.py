"""Momentum meshes and eigenstate sampling for two-dimensional Bloch Hamiltonians.

The Stage-2 topology algorithms work with a stored, periodic momentum mesh rather than
re-diagonalizing the same Hamiltonian inside each individual plaquette calculation.  This makes
FHS links, Kubo curvature, direct-gap diagnostics, and convergence studies share one numerical
source of truth.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from qhe.models import (
    HarperHofstadterParameters,
    MagneticBrillouinZone,
    bloch_hamiltonian,
    magnetic_brillouin_zone,
)

BlochHamiltonian = Callable[[float, float], np.ndarray]


@dataclass(frozen=True, slots=True)
class MomentumMesh:
    """Uniform closed-open mesh on a rectangular momentum domain.

    ``kx`` and ``ky`` use the left endpoint and exclude the right endpoint.  This convention
    makes periodic wrapping exact at the discrete-grid level and avoids duplicate boundary nodes.
    """

    kx: np.ndarray
    ky: np.ndarray
    dkx: float
    dky: float
    zone: MagneticBrillouinZone

    def __post_init__(self) -> None:
        if self.kx.ndim != 1 or self.ky.ndim != 1:
            raise ValueError("MomentumMesh kx and ky must be one-dimensional arrays.")
        if self.kx.size < 2 or self.ky.size < 2:
            raise ValueError("MomentumMesh requires at least two points along each direction.")
        if self.dkx <= 0.0 or self.dky <= 0.0:
            raise ValueError("MomentumMesh spacings must be strictly positive.")

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(N_kx, N_ky)``."""

        return int(self.kx.size), int(self.ky.size)

    @property
    def plaquette_area(self) -> float:
        """Return the area of one momentum-space plaquette."""

        return float(self.dkx * self.dky)


@dataclass(frozen=True, slots=True)
class BandMesh:
    """Eigenvalues and eigenvectors sampled on a :class:`MomentumMesh`.

    Arrays follow the shapes

    - ``energies[N_kx, N_ky, N_band]``;
    - ``eigenvectors[N_kx, N_ky, N_orbital, N_band]``.

    The final axis labels the eigenvector column, matching ``numpy.linalg.eigh``.
    """

    mesh: MomentumMesh
    energies: np.ndarray
    eigenvectors: np.ndarray

    def __post_init__(self) -> None:
        nkx, nky = self.mesh.shape
        if self.energies.ndim != 3:
            raise ValueError("BandMesh energies must have shape (N_kx, N_ky, N_band).")
        if self.eigenvectors.ndim != 4:
            raise ValueError(
                "BandMesh eigenvectors must have shape (N_kx, N_ky, N_orbital, N_band)."
            )
        if self.energies.shape[:2] != (nkx, nky):
            raise ValueError("BandMesh energies do not match the supplied momentum mesh.")
        if self.eigenvectors.shape[:2] != (nkx, nky):
            raise ValueError("BandMesh eigenvectors do not match the supplied momentum mesh.")
        if self.eigenvectors.shape[-1] != self.energies.shape[-1]:
            raise ValueError("BandMesh band count differs between energies and eigenvectors.")
        if self.eigenvectors.shape[-2] != self.energies.shape[-1]:
            raise ValueError("Only square Bloch Hamiltonians are supported by BandMesh.")

    @property
    def band_count(self) -> int:
        """Return the number of isolated-band candidates sampled on the mesh."""

        return int(self.energies.shape[-1])


def uniform_momentum_mesh(
    zone: MagneticBrillouinZone,
    nkx: int,
    nky: int | None = None,
) -> MomentumMesh:
    """Create a uniform periodic mesh for a supplied momentum-space rectangle."""

    if nkx < 2:
        raise ValueError("nkx must be at least 2.")
    resolved_nky = nkx if nky is None else nky
    if resolved_nky < 2:
        raise ValueError("nky must be at least 2.")

    kx = np.linspace(zone.kx_min, zone.kx_max, nkx, endpoint=False, dtype=float)
    ky = np.linspace(zone.ky_min, zone.ky_max, resolved_nky, endpoint=False, dtype=float)
    return MomentumMesh(
        kx=kx,
        ky=ky,
        dkx=float(zone.kx_width / nkx),
        dky=float(zone.ky_width / resolved_nky),
        zone=zone,
    )


def diagonalize_bloch_mesh(hamiltonian: BlochHamiltonian, mesh: MomentumMesh) -> BandMesh:
    """Diagonalize a Hermitian Bloch Hamiltonian once at every mesh node.

    ``hamiltonian`` must return a square Hermitian matrix of fixed dimension for every point of the
    mesh.  Hermiticity is enforced in the model layer; this function verifies shape consistency.
    """

    initial = np.asarray(hamiltonian(float(mesh.kx[0]), float(mesh.ky[0])), dtype=np.complex128)
    if initial.ndim != 2 or initial.shape[0] != initial.shape[1]:
        raise ValueError("Bloch Hamiltonian must return a square rank-2 matrix.")

    orbital_count = int(initial.shape[0])
    nkx, nky = mesh.shape
    energies = np.empty((nkx, nky, orbital_count), dtype=float)
    eigenvectors = np.empty((nkx, nky, orbital_count, orbital_count), dtype=np.complex128)

    for ix, kx in enumerate(mesh.kx):
        for iy, ky in enumerate(mesh.ky):
            matrix = np.asarray(hamiltonian(float(kx), float(ky)), dtype=np.complex128)
            if matrix.shape != (orbital_count, orbital_count):
                raise ValueError("Bloch Hamiltonian changed its matrix dimension across the mesh.")
            values, vectors = np.linalg.eigh(matrix)
            energies[ix, iy] = values
            eigenvectors[ix, iy] = vectors

    return BandMesh(mesh=mesh, energies=energies, eigenvectors=eigenvectors)


def harper_hofstadter_band_mesh(
    parameters: HarperHofstadterParameters | None = None,
    *,
    nkx: int,
    nky: int | None = None,
) -> BandMesh:
    """Sample the canonical Harper-Hofstadter magnetic Bloch Hamiltonian on the MBZ."""

    params = parameters or HarperHofstadterParameters()
    mesh = uniform_momentum_mesh(magnetic_brillouin_zone(params), nkx=nkx, nky=nky)
    return diagonalize_bloch_mesh(
        lambda kx, ky: bloch_hamiltonian(kx, ky, params),
        mesh,
    )


__all__ = [
    "BandMesh",
    "BlochHamiltonian",
    "MomentumMesh",
    "diagonalize_bloch_mesh",
    "harper_hofstadter_band_mesh",
    "uniform_momentum_mesh",
]
