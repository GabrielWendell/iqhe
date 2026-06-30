"""Gauge-invariant topology algorithms and convergence workflows."""

from qhe.topology.convergence import (
    ConvergenceResult,
    CurvatureComparison,
    TopologyAnalysis,
    analyze_harper_hofstadter_topology,
    compare_fhs_and_kubo,
    harper_hofstadter_convergence,
    plaquette_average,
)
from qhe.topology.fhs import FHSResult, fhs_from_band_mesh
from qhe.topology.kubo import (
    KuboResult,
    interband_kubo_curvature_at_point,
    kubo_from_band_mesh,
    minimum_direct_gaps,
)
from qhe.topology.mesh import (
    BandMesh,
    MomentumMesh,
    diagonalize_bloch_mesh,
    harper_hofstadter_band_mesh,
    uniform_momentum_mesh,
)

__all__ = [
    "BandMesh",
    "ConvergenceResult",
    "CurvatureComparison",
    "FHSResult",
    "KuboResult",
    "MomentumMesh",
    "TopologyAnalysis",
    "analyze_harper_hofstadter_topology",
    "compare_fhs_and_kubo",
    "diagonalize_bloch_mesh",
    "fhs_from_band_mesh",
    "harper_hofstadter_band_mesh",
    "harper_hofstadter_convergence",
    "interband_kubo_curvature_at_point",
    "kubo_from_band_mesh",
    "minimum_direct_gaps",
    "plaquette_average",
    "uniform_momentum_mesh",
]
