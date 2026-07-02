"""Ribbon-spectrum calculation and quantitative edge-state diagnostics.

The Stage-3 ribbon is open along x and periodic along y.  Each momentum ``ky`` therefore
produces a finite Hermitian Harper-Hofstadter matrix whose eigenvectors are directly suitable for
left/right edge-participation measurements.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qhe.boundary.geometry import (
    RibbonEdgeMasks,
    inverse_participation_ratio,
    probability_mass,
    ribbon_edge_masks,
)
from qhe.models import HarperHofstadterParameters, ribbon_hamiltonian


@dataclass(frozen=True, slots=True)
class RibbonSpectrum:
    """Diagonalized x-open/y-periodic Harper-Hofstadter ribbon over a closed-open ky mesh."""

    parameters: HarperHofstadterParameters
    lx: int
    edge_masks: RibbonEdgeMasks
    ky: np.ndarray
    energies: np.ndarray
    eigenvectors: np.ndarray
    left_participation: np.ndarray
    right_participation: np.ndarray
    edge_participation: np.ndarray
    edge_polarization: np.ndarray
    inverse_participation: np.ndarray

    def __post_init__(self) -> None:
        nky = self.ky.size
        if self.ky.ndim != 1 or nky < 2:
            raise ValueError("ky must be a one-dimensional mesh with at least two points.")
        expected_spectrum = (nky, self.lx)
        if self.energies.shape != expected_spectrum:
            raise ValueError("Ribbon energy array must have shape (N_ky, lx).")
        if self.eigenvectors.shape != (nky, self.lx, self.lx):
            raise ValueError("Ribbon eigenvectors must have shape (N_ky, lx, lx).")
        for name, array in (
            ("left_participation", self.left_participation),
            ("right_participation", self.right_participation),
            ("edge_participation", self.edge_participation),
            ("edge_polarization", self.edge_polarization),
            ("inverse_participation", self.inverse_participation),
        ):
            if array.shape != expected_spectrum:
                raise ValueError(f"{name} must have shape (N_ky, lx).")
        if self.edge_masks.n_sites != self.lx:
            raise ValueError("Ribbon masks must match the transverse ribbon width.")
        if not np.all(np.isfinite(self.energies)):
            raise ValueError("Ribbon energies must be finite.")
        if np.any(self.edge_participation < -1.0e-12) or np.any(
            self.edge_participation > 1.0 + 1.0e-12
        ):
            raise ValueError("Edge participation must lie in [0, 1] for normalized eigenstates.")

    @property
    def nky(self) -> int:
        """Number of sampled periodic momenta."""

        return int(self.ky.size)

    @property
    def ky_spacing(self) -> float:
        """Uniform closed-open momentum spacing."""

        return float(2.0 * np.pi / (self.parameters.lattice_spacing * self.nky))

    def edge_localized_mask(self, threshold: float = 0.5) -> np.ndarray:
        """Return states with total edge probability at least ``threshold``."""

        if not 0.0 < threshold <= 1.0:
            raise ValueError("threshold must lie in (0, 1].")
        return self.edge_participation >= float(threshold)


def ribbon_momentum_grid(
    nky: int,
    parameters: HarperHofstadterParameters | None = None,
) -> np.ndarray:
    """Return the closed-open crystal-momentum grid ``[-pi/a, pi/a)`` for a ribbon."""

    if nky < 2:
        raise ValueError("nky must be at least two.")
    params = parameters or HarperHofstadterParameters()
    return np.linspace(
        -np.pi / params.lattice_spacing,
        np.pi / params.lattice_spacing,
        int(nky),
        endpoint=False,
        dtype=float,
    )


def diagonalize_ribbon(
    *,
    lx: int,
    nky: int,
    edge_width: int,
    parameters: HarperHofstadterParameters | None = None,
) -> RibbonSpectrum:
    """Diagonalize a ribbon and attach edge-localization diagnostics to every eigenstate.

    The eigenvector convention is inherited from :func:`numpy.linalg.eigh`: the final index of
    ``eigenvectors[iky, :, iband]`` labels the eigenstate column associated with
    ``energies[iky, iband]``.
    """

    params = parameters or HarperHofstadterParameters()
    masks = ribbon_edge_masks(int(lx), int(edge_width))
    ky = ribbon_momentum_grid(int(nky), params)
    energies = np.empty((ky.size, int(lx)), dtype=float)
    eigenvectors = np.empty((ky.size, int(lx), int(lx)), dtype=np.complex128)
    left = np.empty_like(energies)
    right = np.empty_like(energies)
    edge = np.empty_like(energies)
    ipr = np.empty_like(energies)

    for iky, value in enumerate(ky):
        hamiltonian = ribbon_hamiltonian(int(lx), float(value), params)
        eigenvalues, eigenstates = np.linalg.eigh(hamiltonian)
        energies[iky, :] = eigenvalues
        eigenvectors[iky, :, :] = eigenstates
        left[iky, :] = probability_mass(eigenstates, masks.left)
        right[iky, :] = probability_mass(eigenstates, masks.right)
        edge[iky, :] = probability_mass(eigenstates, masks.total)
        ipr[iky, :] = inverse_participation_ratio(eigenstates)

    polarization = left - right
    return RibbonSpectrum(
        parameters=params,
        lx=int(lx),
        edge_masks=masks,
        ky=ky,
        energies=energies,
        eigenvectors=eigenvectors,
        left_participation=left,
        right_participation=right,
        edge_participation=edge,
        edge_polarization=polarization,
        inverse_participation=ipr,
    )


__all__ = ["RibbonSpectrum", "diagonalize_ribbon", "ribbon_momentum_grid"]
