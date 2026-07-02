"""Gauge-invariance and Chern-number tests for FHS topology."""

import numpy as np

from qhe.models import HarperHofstadterParameters
from qhe.topology import BandMesh, fhs_from_band_mesh, harper_hofstadter_band_mesh


def test_fhs_returns_expected_phi_one_third_chern_numbers() -> None:
    sampled = harper_hofstadter_band_mesh(HarperHofstadterParameters(p=1, q=3), nkx=21)
    result = fhs_from_band_mesh(sampled)

    assert np.allclose(result.chern_numbers, np.array([-1.0, 2.0, -1.0]), atol=1.0e-10)
    assert np.isclose(np.sum(result.chern_numbers), 0.0, atol=1.0e-10)
    assert result.minimum_link_modulus > 1.0e-2


def test_fhs_is_invariant_under_local_u_one_eigenvector_phases() -> None:
    sampled = harper_hofstadter_band_mesh(HarperHofstadterParameters(p=1, q=3), nkx=17)
    reference = fhs_from_band_mesh(sampled)

    rng = np.random.default_rng(20260629)
    phases = rng.uniform(-np.pi, np.pi, size=sampled.energies.shape)
    transformed_vectors = sampled.eigenvectors * np.exp(1.0j * phases)[..., np.newaxis, :]
    transformed = BandMesh(
        mesh=sampled.mesh,
        energies=sampled.energies.copy(),
        eigenvectors=transformed_vectors,
    )
    result = fhs_from_band_mesh(transformed)

    assert np.allclose(result.plaquette_flux, reference.plaquette_flux, atol=1.0e-12)
    assert np.allclose(result.chern_numbers, reference.chern_numbers, atol=1.0e-12)
