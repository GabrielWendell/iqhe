"""Stage-1 regression tests for the canonical Harper-Hofstadter Hamiltonian family."""

import numpy as np
import pytest

from qhe.models import (
    HarperHofstadterParameters,
    bloch_hamiltonian,
    bloch_hamiltonian_derivatives,
    magnetic_brillouin_zone,
    open_hamiltonian,
    peierls_phase,
    ribbon_hamiltonian,
    site_coordinates,
    site_index,
)
from qhe.validation import assert_hermitian


@pytest.fixture
def params() -> HarperHofstadterParameters:
    return HarperHofstadterParameters(p=1, q=3, tx=1.25, ty=0.85, lattice_spacing=1.0)


def test_flux_parameters_require_coprime_integers() -> None:
    with pytest.raises(ValueError, match='coprime'):
        HarperHofstadterParameters(p=2, q=4)
    with pytest.raises(ValueError, match='positive'):
        HarperHofstadterParameters(p=1, q=0)


def test_peierls_phase_has_magnetic_period(params: HarperHofstadterParameters) -> None:
    assert np.allclose(peierls_phase(2, params), peierls_phase(2 + params.q, params))


def test_site_indexing_is_bijective_for_rectangular_lattice() -> None:
    lx, ly = 4, 7
    indices = {site_index(m, n, ly) for m in range(lx) for n in range(ly)}
    assert indices == set(range(lx * ly))
    assert site_coordinates(site_index(3, 6, ly), ly) == (3, 6)


def test_open_hamiltonian_is_hermitian_and_uses_forward_y_peierls_phase(
    params: HarperHofstadterParameters,
) -> None:
    lx, ly = 4, 5
    matrix = open_hamiltonian(lx, ly, params)
    assert_hermitian(matrix)
    origin = site_index(2, 1, ly)
    up = site_index(2, 2, ly)
    assert np.allclose(matrix[up, origin], -params.ty * peierls_phase(2, params))
    assert np.allclose(matrix[origin, up], np.conjugate(matrix[up, origin]))


@pytest.mark.parametrize('kx, ky', [(0.0, 0.0), (0.17, -0.33), (-0.4, 0.8)])
def test_bloch_hamiltonian_is_hermitian(
    params: HarperHofstadterParameters,
    kx: float,
    ky: float,
) -> None:
    assert_hermitian(bloch_hamiltonian(kx, ky, params))


@pytest.mark.parametrize('ky', [-1.2, 0.0, 1.1])
def test_ribbon_hamiltonian_is_hermitian(
    params: HarperHofstadterParameters,
    ky: float,
) -> None:
    assert_hermitian(ribbon_hamiltonian(8, ky, params))


def test_magnetic_brillouin_zone_matches_magnetic_period(params: HarperHofstadterParameters) -> None:
    zone = magnetic_brillouin_zone(params)
    assert np.isclose(zone.kx_width, 2.0 * np.pi / params.q)
    assert np.isclose(zone.ky_width, 2.0 * np.pi)


def test_bloch_derivatives_match_centered_finite_differences(
    params: HarperHofstadterParameters,
) -> None:
    kx, ky, step = 0.19, -0.47, 1.0e-7
    d_kx, d_ky = bloch_hamiltonian_derivatives(kx, ky, params)
    finite_kx = (bloch_hamiltonian(kx + step, ky, params) - bloch_hamiltonian(kx - step, ky, params)) / (2.0 * step)
    finite_ky = (bloch_hamiltonian(kx, ky + step, params) - bloch_hamiltonian(kx, ky - step, params)) / (2.0 * step)
    assert np.allclose(d_kx, finite_kx, atol=1.0e-7, rtol=1.0e-7)
    assert np.allclose(d_ky, finite_ky, atol=1.0e-7, rtol=1.0e-7)


def test_zero_flux_single_site_magnetic_cell_is_supported() -> None:
    params = HarperHofstadterParameters(p=0, q=1)
    matrix = bloch_hamiltonian(0.31, -0.24, params)
    expected = -2.0 * np.cos(0.31) - 2.0 * np.cos(-0.24)
    assert matrix.shape == (1, 1)
    assert np.allclose(matrix[0, 0], expected)
