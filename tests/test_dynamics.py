"""Regression tests for Stage-6 chiral wave-packet dynamics."""

from __future__ import annotations

import numpy as np

from qhe.dynamics import (
    DynamicsConfig,
    GaussianPacket,
    WeakLinkDefect,
    analyze_chiral_dynamics,
    apply_weak_link_defect,
    bond_currents,
    boundary_link_sites,
    evolve_spectral,
    gaussian_edge_seed,
    normalize_state,
    norm_diagnostics,
    side_current_indicator,
)
from qhe.dynamics.evolution import diagonalize_hamiltonian
from qhe.models import HarperHofstadterParameters, open_hamiltonian


def test_gaussian_edge_seed_is_normalized_and_phase_sensitive() -> None:
    packet_a = GaussianPacket(side="left", momentum=-1.0, sigma_longitudinal=3.0)
    packet_b = GaussianPacket(side="left", momentum=0.5, sigma_longitudinal=3.0)
    state_a = gaussian_edge_seed(8, 18, packet_a)
    state_b = gaussian_edge_seed(8, 18, packet_b)
    assert np.isclose(np.vdot(state_a, state_a).real, 1.0)
    assert np.isclose(np.vdot(state_b, state_b).real, 1.0)
    assert abs(np.vdot(state_a, state_b)) < 0.95


def test_spectral_evolution_conserves_norm_without_manual_renormalization() -> None:
    hamiltonian = np.array([[0.0, 1.0j], [-1.0j, 0.0]], dtype=np.complex128)
    decomposition = diagonalize_hamiltonian(hamiltonian)
    initial = normalize_state(np.array([1.0, 1.0], dtype=np.complex128))
    states = evolve_spectral(decomposition, initial, np.linspace(0.0, 3.0, 17))
    diagnostics = norm_diagnostics(states)
    assert diagnostics.max_deviation < 1.0e-12


def test_weak_link_defect_preserves_hermiticity_and_changes_one_link() -> None:
    params = HarperHofstadterParameters(p=1, q=3)
    hamiltonian = open_hamiltonian(8, 12, params)
    defect = WeakLinkDefect(side="left", position=4, factor=0.0)
    first, second = boundary_link_sites(8, 12, defect)
    modified = apply_weak_link_defect(hamiltonian, 8, 12, defect)
    assert np.allclose(modified, modified.conj().T)
    assert hamiltonian[first, second] != 0.0
    assert modified[first, second] == 0.0
    untouched = np.array(hamiltonian, copy=True)
    untouched[first, second] = 0.0
    untouched[second, first] = 0.0
    comparison = np.array(modified, copy=True)
    comparison[first, second] = 0.0
    comparison[second, first] = 0.0
    assert np.allclose(untouched, comparison)


def test_bond_current_indicator_has_expected_sign_for_stage6_packet() -> None:
    analysis = analyze_chiral_dynamics(
        DynamicsConfig(
            lx=8,
            ly=18,
            edge_width=2,
            sigma_longitudinal=3.5,
            time_final=3.0,
            n_times=25,
            fit_until=1.5,
            ribbon_lx=24,
            ribbon_nky=81,
            bulk_nkx=15,
        )
    )
    currents = bond_currents(
        analysis.clean.states[0],
        analysis.config.lx,
        analysis.config.ly,
        analysis.config.parameters,
    )
    indicator = side_current_indicator(currents, analysis.config.side, edge_width=2)
    assert indicator * analysis.group_velocity > 0.0


def test_stage6_default_like_analysis_meets_core_thresholds() -> None:
    analysis = analyze_chiral_dynamics(
        DynamicsConfig(
            lx=8,
            ly=18,
            edge_width=2,
            sigma_longitudinal=3.5,
            time_final=3.0,
            n_times=25,
            fit_until=1.5,
            ribbon_lx=24,
            ribbon_nky=81,
            bulk_nkx=15,
        )
    )
    assert analysis.clean.norms.max_deviation < 1.0e-12
    assert analysis.defect.norms.max_deviation < 1.0e-12
    assert analysis.clean.initial_edge_probability > 0.85
    assert analysis.clean.mean_edge_probability > 0.80
    assert analysis.defect.mean_edge_probability > 0.75
    assert analysis.relative_velocity_error < 0.10
    assert analysis.defect_relative_velocity_error < 0.35
