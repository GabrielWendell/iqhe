"""Fukui-Hatsugai-Suzuki discrete Berry-flux calculations.

The frozen project convention uses ``A = i<u|grad u>``.  With that convention, an overlap link
``<u(k)|u(k+dk)>`` carries the phase ``-A.dk``.  The FHS plaquette phase is therefore negated here
so that the resulting discrete flux approximates the Berry-curvature density defined in
:mod:`qhe.conventions`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qhe.topology.mesh import BandMesh


@dataclass(frozen=True, slots=True)
class FHSResult:
    """Gauge-invariant FHS outputs for every isolated band on a sampled mesh."""

    plaquette_flux: np.ndarray
    curvature_density: np.ndarray
    chern_numbers: np.ndarray
    minimum_link_modulus: float

    def __post_init__(self) -> None:
        if self.plaquette_flux.ndim != 3:
            raise ValueError("FHS plaquette_flux must have shape (N_kx, N_ky, N_band).")
        if self.curvature_density.shape != self.plaquette_flux.shape:
            raise ValueError("FHS curvature_density must match plaquette_flux shape.")
        if self.chern_numbers.shape != (self.plaquette_flux.shape[-1],):
            raise ValueError("FHS chern_numbers must have one entry per band.")


def fhs_from_band_mesh(
    band_mesh: BandMesh,
    *,
    overlap_floor: float = 1.0e-12,
) -> FHSResult:
    """Compute FHS fluxes, curvature densities, and Chern numbers from stored eigenvectors.

    The calculation includes periodic wrapping in both mesh directions.  It raises when a link
    overlap is too small to define a stable ``U(1)`` link variable. Such a failure indicates that
    mesh must be refined, the bands must be treated as a multiplet, or a gap is closing.
    """

    if overlap_floor <= 0.0:
        raise ValueError("overlap_floor must be strictly positive.")

    vectors = band_mesh.eigenvectors
    overlap_x = np.sum(
        np.conjugate(vectors) * np.roll(vectors, shift=-1, axis=0),
        axis=2,
    )
    overlap_y = np.sum(
        np.conjugate(vectors) * np.roll(vectors, shift=-1, axis=1),
        axis=2,
    )
    link_moduli = np.concatenate((np.abs(overlap_x).ravel(), np.abs(overlap_y).ravel()))
    minimum_link_modulus = float(np.min(link_moduli))
    if minimum_link_modulus < overlap_floor:
        raise ValueError(
            "Encountered a near-zero FHS overlap link: "
            f"minimum modulus={minimum_link_modulus:.3e}, floor={overlap_floor:.3e}."
        )

    link_x = overlap_x / np.abs(overlap_x)
    link_y = overlap_y / np.abs(overlap_y)
    oriented_product = (
        link_x
        * np.roll(link_y, shift=-1, axis=0)
        * np.conjugate(np.roll(link_x, shift=-1, axis=1))
        * np.conjugate(link_y)
    )

    # The leading minus sign is required by the frozen A=i<u|grad u> convention.
    plaquette_flux = -np.angle(oriented_product)
    curvature_density = plaquette_flux / band_mesh.mesh.plaquette_area
    chern_numbers = np.sum(plaquette_flux, axis=(0, 1)) / (2.0 * np.pi)

    return FHSResult(
        plaquette_flux=plaquette_flux,
        curvature_density=curvature_density,
        chern_numbers=chern_numbers,
        minimum_link_modulus=minimum_link_modulus,
    )


__all__ = ["FHSResult", "fhs_from_band_mesh"]
