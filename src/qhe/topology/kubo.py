"""Interband Kubo Berry-curvature calculations for isolated Bloch bands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from qhe.topology.mesh import BandMesh

BlochDerivatives = Callable[[float, float], tuple[np.ndarray, np.ndarray]]


@dataclass(frozen=True, slots=True)
class KuboResult:
    """Pointwise interband-Kubo curvature and its mesh-integrated Chern estimates."""

    curvature_density: np.ndarray
    chern_numbers: np.ndarray
    minimum_direct_gaps: np.ndarray

    def __post_init__(self) -> None:
        if self.curvature_density.ndim != 3:
            raise ValueError("Kubo curvature_density must have shape (N_kx, N_ky, N_band).")
        if self.chern_numbers.shape != (self.curvature_density.shape[-1],):
            raise ValueError("Kubo chern_numbers must have one entry per band.")
        if self.minimum_direct_gaps.shape != (self.curvature_density.shape[-1] - 1,):
            raise ValueError(
                "Kubo minimum_direct_gaps must have one entry per adjacent band pair."
            )


def minimum_direct_gaps(energies: np.ndarray) -> np.ndarray:
    """Return the minimum direct gap for each adjacent energy-band pair on a mesh."""

    array = np.asarray(energies, dtype=float)
    if array.ndim != 3 or array.shape[-1] < 2:
        raise ValueError("energies must have shape (N_kx, N_ky, N_band) with N_band >= 2.")
    local_gaps = np.diff(array, axis=-1)
    return np.min(local_gaps, axis=(0, 1))


def interband_kubo_curvature_at_point(
    energies: np.ndarray,
    eigenvectors: np.ndarray,
    d_hamiltonian_dkx: np.ndarray,
    d_hamiltonian_dky: np.ndarray,
    *,
    degeneracy_tolerance: float = 1.0e-12,
) -> np.ndarray:
    r"""Evaluate the isolated-band interband Kubo curvature at one momentum point.

    The implemented expression is

    .. math::

       \Omega_n = -2\,\mathrm{Im}\sum_{m\ne n}
       \frac{\langle n|\partial_{k_x}H|m\rangle
       \langle m|\partial_{k_y}H|n\rangle}{(E_m-E_n)^2}.

    It is consistent with the frozen convention ``A=i<u|grad u>``.
    """

    values = np.asarray(energies, dtype=float)
    vectors = np.asarray(eigenvectors, dtype=np.complex128)
    derivative_x = np.asarray(d_hamiltonian_dkx, dtype=np.complex128)
    derivative_y = np.asarray(d_hamiltonian_dky, dtype=np.complex128)
    band_count = values.size

    if vectors.shape != (band_count, band_count):
        raise ValueError("eigenvectors must be square with one eigenvector column per band.")
    if derivative_x.shape != (band_count, band_count):
        raise ValueError("d_hamiltonian_dkx has incompatible shape.")
    if derivative_y.shape != (band_count, band_count):
        raise ValueError("d_hamiltonian_dky has incompatible shape.")
    if degeneracy_tolerance <= 0.0:
        raise ValueError("degeneracy_tolerance must be strictly positive.")

    velocity_x = vectors.conj().T @ derivative_x @ vectors
    velocity_y = vectors.conj().T @ derivative_y @ vectors
    curvature = np.zeros(band_count, dtype=float)

    for band in range(band_count):
        energy_difference = values - values[band]
        mask = np.ones(band_count, dtype=bool)
        mask[band] = False
        minimum_separation = float(np.min(np.abs(energy_difference[mask])))
        if minimum_separation < degeneracy_tolerance:
            raise ValueError(
                "Interband Kubo curvature is undefined at a numerical degeneracy: "
                f"minimum separation={minimum_separation:.3e}, "
                f"tolerance={degeneracy_tolerance:.3e}."
            )
        numerator = velocity_x[band, mask] * velocity_y[mask, band]
        curvature[band] = float(
            -2.0 * np.imag(np.sum(numerator / energy_difference[mask] ** 2))
        )

    return curvature


def kubo_from_band_mesh(
    band_mesh: BandMesh,
    derivatives: BlochDerivatives,
    *,
    degeneracy_tolerance: float = 1.0e-12,
) -> KuboResult:
    """Evaluate interband Kubo curvature across a stored :class:`BandMesh`."""

    nkx, nky = band_mesh.mesh.shape
    band_count = band_mesh.band_count
    curvature = np.empty((nkx, nky, band_count), dtype=float)

    for ix, kx in enumerate(band_mesh.mesh.kx):
        for iy, ky in enumerate(band_mesh.mesh.ky):
            derivative_x, derivative_y = derivatives(float(kx), float(ky))
            curvature[ix, iy] = interband_kubo_curvature_at_point(
                band_mesh.energies[ix, iy],
                band_mesh.eigenvectors[ix, iy],
                derivative_x,
                derivative_y,
                degeneracy_tolerance=degeneracy_tolerance,
            )

    chern_numbers = (
        np.sum(curvature, axis=(0, 1)) * band_mesh.mesh.plaquette_area / (2.0 * np.pi)
    )
    return KuboResult(
        curvature_density=curvature,
        chern_numbers=chern_numbers,
        minimum_direct_gaps=minimum_direct_gaps(band_mesh.energies),
    )


__all__ = [
    "BlochDerivatives",
    "KuboResult",
    "interband_kubo_curvature_at_point",
    "kubo_from_band_mesh",
    "minimum_direct_gaps",
]
