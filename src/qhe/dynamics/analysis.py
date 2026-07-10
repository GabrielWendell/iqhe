"""End-to-end Stage 6 chiral edge-wave-packet dynamics workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from qhe.boundary import BulkBoundaryAnalysis, EdgeCrossing, analyze_bulk_boundary_correspondence
from qhe.boundary.geometry import OpenSideMasks, open_side_masks
from qhe.dynamics.currents import bond_currents, side_current_indicator
from qhe.dynamics.defects import WeakLinkDefect, apply_weak_link_defect
from qhe.dynamics.evolution import (
    NormDiagnostics,
    SpectralDecomposition,
    diagonalize_hamiltonian,
    evolve_spectral,
    norm_diagnostics,
)
from qhe.dynamics.observables import (
    VelocityFit,
    bulk_leakage,
    edge_coordinate_timeseries,
    estimate_velocity,
    probability_timeseries,
)
from qhe.dynamics.packets import (
    EdgeSide,
    GaussianPacket,
    edge_gap_selection,
    gaussian_edge_seed,
    project_onto_subspace,
)
from qhe.models import HarperHofstadterParameters, open_hamiltonian
from qhe.validation import assert_hermitian

GapSelector = Literal[0, 1]


@dataclass(frozen=True, slots=True)
class DynamicsConfig:
    """Numerical parameters for the frozen Stage 6 validation case."""

    parameters: HarperHofstadterParameters = HarperHofstadterParameters()
    gap_index: GapSelector = 0
    side: EdgeSide = "left"
    lx: int = 12
    ly: int = 30
    edge_width: int = 2
    sigma_transverse: float = 0.8
    sigma_longitudinal: float = 5.0
    center_longitudinal: float = 0.50
    offset_from_boundary: float = 0.5
    time_final: float = 4.0
    n_times: int = 41
    fit_until: float = 2.0
    minimum_side_participation: float = 0.20
    bulk_nkx: int = 15
    ribbon_lx: int = 24
    ribbon_nky: int = 81
    ribbon_edge_threshold: float = 0.50
    defect_factor: float = 0.0
    hbar: float = 1.0

    def __post_init__(self) -> None:
        if self.gap_index not in {0, 1}:
            raise ValueError("gap_index must be 0 or 1 for the phi=1/3 reference model.")
        if self.side not in {"left", "right", "bottom", "top"}:
            raise ValueError("side must be 'left', 'right', 'bottom', or 'top'.")
        if self.side in {"bottom", "top"}:
            raise ValueError("Stage 6 currently validates left/right ribbon-compatible edges.")
        if self.lx <= 1 or self.ly <= 2:
            raise ValueError("lx and ly are too small for an open finite lattice.")
        if self.n_times < 3 or self.time_final <= 0.0:
            raise ValueError("At least three positive-time samples are required.")
        if self.hbar <= 0.0:
            raise ValueError("hbar must be strictly positive.")

    @property
    def times(self) -> np.ndarray:
        return np.linspace(0.0, self.time_final, self.n_times, dtype=float)


@dataclass(frozen=True, slots=True)
class DynamicsRun:
    """One time-domain propagation record."""

    hamiltonian: np.ndarray
    spectrum: SpectralDecomposition
    states: np.ndarray
    norms: NormDiagnostics
    side_probability: np.ndarray
    edge_probability: np.ndarray
    bulk_probability: np.ndarray
    coordinate: np.ndarray
    velocity_fit: VelocityFit
    initial_state: np.ndarray
    side_current_initial: float
    selected_state_count: int

    @property
    def initial_edge_probability(self) -> float:
        return float(self.edge_probability[0])

    @property
    def mean_edge_probability(self) -> float:
        return float(np.mean(self.edge_probability))

    @property
    def mean_side_probability(self) -> float:
        return float(np.mean(self.side_probability))


@dataclass(frozen=True, slots=True)
class DynamicsAnalysis:
    """Complete clean/defect Stage 6 validation result."""

    config: DynamicsConfig
    bulk_boundary: BulkBoundaryAnalysis
    crossing: EdgeCrossing
    side_masks: OpenSideMasks
    clean: DynamicsRun
    defect: DynamicsRun
    weak_link: WeakLinkDefect

    @property
    def group_velocity(self) -> float:
        return float(self.crossing.slope / self.config.hbar)

    @property
    def relative_velocity_error(self) -> float:
        scale = max(abs(self.group_velocity), 1.0e-12)
        return float(abs(self.clean.velocity_fit.velocity - self.group_velocity) / scale)

    @property
    def defect_relative_velocity_error(self) -> float:
        scale = max(abs(self.group_velocity), 1.0e-12)
        return float(abs(self.defect.velocity_fit.velocity - self.group_velocity) / scale)


def _select_crossing(
    analysis: BulkBoundaryAnalysis,
    gap_index: int,
    side: EdgeSide,
) -> EdgeCrossing:
    summary = analysis.crossing_summaries[int(gap_index)]
    crossings = summary.left_crossings if side == "left" else summary.right_crossings
    if not crossings:
        raise ValueError(f"No {side} crossing found for gap {gap_index}.")
    return crossings[0]


def _defect_position(config: DynamicsConfig, group_velocity: float) -> int:
    center = config.center_longitudinal * (config.ly - 1)
    target = center + group_velocity * (0.5 * config.time_final)
    return int(np.clip(round(target), config.edge_width + 1, config.ly - config.edge_width - 3))


def _run_single_dynamics(
    hamiltonian: np.ndarray,
    seed: np.ndarray,
    config: DynamicsConfig,
    side_masks: OpenSideMasks,
    gap_index: int,
    bulk_boundary: BulkBoundaryAnalysis,
) -> DynamicsRun:
    assert_hermitian(hamiltonian)
    spectrum = diagonalize_hamiltonian(hamiltonian)
    side_mask = side_masks.side(config.side)
    gap = bulk_boundary.gaps[int(gap_index)]
    selected = edge_gap_selection(
        spectrum.energies,
        spectrum.eigenvectors,
        gap,
        side_mask,
        minimum_side_participation=config.minimum_side_participation,
    )
    initial_state, _ = project_onto_subspace(seed, spectrum.eigenvectors[:, selected])
    states = evolve_spectral(spectrum, initial_state, config.times, hbar=config.hbar)
    norms = norm_diagnostics(states)
    side_probability = probability_timeseries(states, side_mask)
    edge_probability = probability_timeseries(states, side_masks.perimeter)
    bulk_probability = bulk_leakage(edge_probability)
    coordinate = edge_coordinate_timeseries(
        states,
        config.lx,
        config.ly,
        config.side,
        side_mask,
    )
    velocity_fit = estimate_velocity(config.times, coordinate, fit_until=config.fit_until)
    currents = bond_currents(states[0], config.lx, config.ly, config.parameters, hbar=config.hbar)
    return DynamicsRun(
        hamiltonian=np.asarray(hamiltonian, dtype=np.complex128),
        spectrum=spectrum,
        states=states,
        norms=norms,
        side_probability=side_probability,
        edge_probability=edge_probability,
        bulk_probability=bulk_probability,
        coordinate=coordinate,
        velocity_fit=velocity_fit,
        initial_state=initial_state,
        side_current_initial=side_current_indicator(
            currents,
            config.side,
            edge_width=config.edge_width,
        ),
        selected_state_count=int(np.count_nonzero(selected)),
    )


def analyze_chiral_dynamics(config: DynamicsConfig | None = None) -> DynamicsAnalysis:
    """Run the Stage 6 clean and weak-link-defect chiral-dynamics workflow."""

    resolved = config or DynamicsConfig()
    bulk_boundary = analyze_bulk_boundary_correspondence(
        resolved.parameters,
        bulk_nkx=resolved.bulk_nkx,
        bulk_nky=resolved.bulk_nkx,
        ribbon_lx=resolved.ribbon_lx,
        ribbon_nky=resolved.ribbon_nky,
        edge_width=resolved.edge_width,
        edge_threshold=resolved.ribbon_edge_threshold,
    )
    crossing = _select_crossing(bulk_boundary, resolved.gap_index, resolved.side)
    packet = GaussianPacket(
        side=resolved.side,
        center_longitudinal=resolved.center_longitudinal,
        offset_from_boundary=resolved.offset_from_boundary,
        sigma_transverse=resolved.sigma_transverse,
        sigma_longitudinal=resolved.sigma_longitudinal,
        momentum=crossing.ky,
    )
    seed = gaussian_edge_seed(resolved.lx, resolved.ly, packet)
    masks = open_side_masks(resolved.lx, resolved.ly, resolved.edge_width)
    clean_hamiltonian = open_hamiltonian(resolved.lx, resolved.ly, resolved.parameters)
    clean = _run_single_dynamics(
        clean_hamiltonian,
        seed,
        resolved,
        masks,
        resolved.gap_index,
        bulk_boundary,
    )
    defect = WeakLinkDefect(
        side=resolved.side,
        position=_defect_position(resolved, crossing.slope / resolved.hbar),
        factor=resolved.defect_factor,
    )
    defect_hamiltonian = apply_weak_link_defect(
        clean_hamiltonian,
        resolved.lx,
        resolved.ly,
        defect,
    )
    defect_run = _run_single_dynamics(
        defect_hamiltonian,
        seed,
        resolved,
        masks,
        resolved.gap_index,
        bulk_boundary,
    )
    return DynamicsAnalysis(
        config=resolved,
        bulk_boundary=bulk_boundary,
        crossing=crossing,
        side_masks=masks,
        clean=clean,
        defect=defect_run,
        weak_link=defect,
    )


__all__ = [
    "DynamicsAnalysis",
    "DynamicsConfig",
    "DynamicsRun",
    "analyze_chiral_dynamics",
]
