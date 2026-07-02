"""Tests for periodic momentum meshes and one-pass Bloch diagonalization."""

import numpy as np

from qhe.models import HarperHofstadterParameters, magnetic_brillouin_zone
from qhe.topology import harper_hofstadter_band_mesh, uniform_momentum_mesh


def test_uniform_mesh_is_closed_open_and_has_expected_spacing() -> None:
    params = HarperHofstadterParameters(p=1, q=3)
    zone = magnetic_brillouin_zone(params)
    mesh = uniform_momentum_mesh(zone, nkx=9, nky=12)

    assert mesh.shape == (9, 12)
    assert np.isclose(mesh.kx[0], zone.kx_min)
    assert np.isclose(mesh.ky[0], zone.ky_min)
    assert mesh.kx[-1] < zone.kx_max
    assert mesh.ky[-1] < zone.ky_max
    assert np.isclose(mesh.dkx, zone.kx_width / 9)
    assert np.isclose(mesh.dky, zone.ky_width / 12)


def test_harper_hofstadter_band_mesh_has_expected_shapes_and_band_order() -> None:
    params = HarperHofstadterParameters(p=1, q=3)
    sampled = harper_hofstadter_band_mesh(params, nkx=11, nky=13)

    assert sampled.energies.shape == (11, 13, 3)
    assert sampled.eigenvectors.shape == (11, 13, 3, 3)
    assert np.all(np.diff(sampled.energies, axis=-1) > 0.0)
