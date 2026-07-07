"""Cross-validation and mesh-convergence workflows for Stage-2 topology results."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from qhe.models import HarperHofstadterParameters, bloch_hamiltonian_derivatives
from qhe.topology.fhs import FHSResult, fhs_from_band_mesh
from qhe.topology.kubo import KuboResult, kubo_from_band_mesh
from qhe.topology.mesh import BandMesh, harper_hofstadter_band_mesh


@dataclass(frozen=True, slots=True)
class CurvatureComparison:
    """Compatible FHS-versus-Kubo curvature-density comparison on matching plaquettes."""

    kubo_plaquette_average: np.ndarray
    residual: np.ndarray
    l2_error: np.ndarray
    linf_error: np.ndarray

    def __post_init__(self) -> None:
        if self.kubo_plaquette_average.shape != self.residual.shape:
            raise ValueError("Kubo plaquette average and residual shapes must agree.")
        if self.residual.ndim != 3:
            raise ValueError("Curvature residual must have shape (N_kx, N_ky, N_band).")
        if self.l2_error.shape != (self.residual.shape[-1],):
            raise ValueError("L2 error must contain one value per band.")
        if self.linf_error.shape != (self.residual.shape[-1],):
            raise ValueError("Linf error must contain one value per band.")


@dataclass(frozen=True, slots=True)
class TopologyAnalysis:
    """All topological outputs for one Harper-Hofstadter momentum-mesh resolution."""

    band_mesh: BandMesh
    fhs: FHSResult
    kubo: KuboResult
    comparison: CurvatureComparison


@dataclass(frozen=True, slots=True)
class ConvergenceResult:
    """Mesh-refinement record for independent FHS and interband-Kubo calculations."""

    mesh_sizes: np.ndarray
    fhs_chern_numbers: np.ndarray
    kubo_chern_numbers: np.ndarray
    minimum_direct_gaps: np.ndarray
    l2_errors: np.ndarray
    linf_errors: np.ndarray

    def __post_init__(self) -> None:
        resolution_count = self.mesh_sizes.size
        if self.mesh_sizes.ndim != 1 or resolution_count == 0:
            raise ValueError("mesh_sizes must be a non-empty one-dimensional array.")
        if self.fhs_chern_numbers.shape[0] != resolution_count:
            raise ValueError("FHS convergence rows must match mesh_sizes.")
        if self.kubo_chern_numbers.shape != self.fhs_chern_numbers.shape:
            raise ValueError("Kubo and FHS Chern arrays must have matching shapes.")
        if self.minimum_direct_gaps.shape[0] != resolution_count:
            raise ValueError("Gap convergence rows must match mesh_sizes.")
        if self.l2_errors.shape != self.fhs_chern_numbers.shape:
            raise ValueError("L2 errors must have one row and band entry per mesh size.")
        if self.linf_errors.shape != self.fhs_chern_numbers.shape:
            raise ValueError("Linf errors must have one row and band entry per mesh size.")


def plaquette_average(field: np.ndarray) -> np.ndarray:
    """Average a pointwise periodic field over the four vertices of each plaquette."""

    array = np.asarray(field, dtype=float)
    if array.ndim != 3:
        raise ValueError("field must have shape (N_kx, N_ky, N_band).")
    return 0.25 * (
        array
        + np.roll(array, shift=-1, axis=0)
        + np.roll(array, shift=-1, axis=1)
        + np.roll(np.roll(array, shift=-1, axis=0), shift=-1, axis=1)
    )


def compare_fhs_and_kubo(fhs: FHSResult, kubo: KuboResult) -> CurvatureComparison:
    """Compare FHS curvature density with Kubo curvature averaged on matching plaquettes."""

    kubo_average = plaquette_average(kubo.curvature_density)
    residual = fhs.curvature_density - kubo_average
    l2_error = np.sqrt(np.mean(residual**2, axis=(0, 1)))
    linf_error = np.max(np.abs(residual), axis=(0, 1))
    return CurvatureComparison(
        kubo_plaquette_average=kubo_average,
        residual=residual,
        l2_error=l2_error,
        linf_error=linf_error,
    )


def analyze_harper_hofstadter_topology(
    parameters: HarperHofstadterParameters | None = None,
    *,
    nkx: int,
    nky: int | None = None,
    overlap_floor: float = 1.0e-12,
    degeneracy_tolerance: float = 1.0e-12,
) -> TopologyAnalysis:
    """Run a compatible FHS/Kubo calculation on one canonical Harper-Hofstadter mesh."""

    params = parameters or HarperHofstadterParameters()
    band_mesh = harper_hofstadter_band_mesh(params, nkx=nkx, nky=nky)
    fhs = fhs_from_band_mesh(band_mesh, overlap_floor=overlap_floor)
    kubo = kubo_from_band_mesh(
        band_mesh,
        lambda kx, ky: bloch_hamiltonian_derivatives(kx, ky, params),
        degeneracy_tolerance=degeneracy_tolerance,
    )
    comparison = compare_fhs_and_kubo(fhs, kubo)
    return TopologyAnalysis(band_mesh=band_mesh, fhs=fhs, kubo=kubo, comparison=comparison)


def harper_hofstadter_convergence(
    parameters: HarperHofstadterParameters | None = None,
    *,
    mesh_sizes: Iterable[int] = (21, 41, 81),
    overlap_floor: float = 1.0e-12,
    degeneracy_tolerance: float = 1.0e-12,
) -> ConvergenceResult:
    """Run Stage-2 topology validation over a sequence of square momentum meshes."""

    resolved_sizes = np.asarray(tuple(int(size) for size in mesh_sizes), dtype=int)
    if resolved_sizes.ndim != 1 or resolved_sizes.size == 0:
        raise ValueError("mesh_sizes must contain at least one positive integer.")
    if np.any(resolved_sizes < 2):
        raise ValueError("Every mesh size must be at least 2.")
    if np.any(np.diff(resolved_sizes) <= 0):
        raise ValueError("mesh_sizes must be strictly increasing.")

    analyses = [
        analyze_harper_hofstadter_topology(
            parameters,
            nkx=int(size),
            nky=int(size),
            overlap_floor=overlap_floor,
            degeneracy_tolerance=degeneracy_tolerance,
        )
        for size in resolved_sizes
    ]
    return ConvergenceResult(
        mesh_sizes=resolved_sizes,
        fhs_chern_numbers=np.stack([analysis.fhs.chern_numbers for analysis in analyses]),
        kubo_chern_numbers=np.stack([analysis.kubo.chern_numbers for analysis in analyses]),
        minimum_direct_gaps=np.stack([analysis.kubo.minimum_direct_gaps for analysis in analyses]),
        l2_errors=np.stack([analysis.comparison.l2_error for analysis in analyses]),
        linf_errors=np.stack([analysis.comparison.linf_error for analysis in analyses]),
    )


__all__ = [
    "ConvergenceResult",
    "CurvatureComparison",
    "TopologyAnalysis",
    "analyze_harper_hofstadter_topology",
    "compare_fhs_and_kubo",
    "harper_hofstadter_convergence",
    "plaquette_average",
]
