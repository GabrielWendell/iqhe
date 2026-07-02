"""Stage-3 tests for finite-ribbon spectra and edge measurements."""

import numpy as np

from qhe.boundary import diagonalize_ribbon, ribbon_momentum_grid
from qhe.models import HarperHofstadterParameters


def test_ribbon_momentum_grid_is_closed_open_and_uniform() -> None:
    params = HarperHofstadterParameters()
    ky = ribbon_momentum_grid(16, params)
    assert np.isclose(ky[0], -np.pi)
    assert ky[-1] < np.pi
    assert np.allclose(np.diff(ky), np.diff(ky)[0])


def test_ribbon_spectrum_has_normalized_edge_metrics() -> None:
    result = diagonalize_ribbon(
        lx=24,
        nky=31,
        edge_width=3,
        parameters=HarperHofstadterParameters(p=1, q=3),
    )
    assert result.energies.shape == (31, 24)
    assert result.eigenvectors.shape == (31, 24, 24)
    assert np.all(np.diff(result.energies, axis=1) >= -1.0e-12)
    assert np.allclose(
        result.edge_participation,
        result.left_participation + result.right_participation,
        atol=1.0e-12,
    )
    assert np.all(result.edge_participation >= 0.0)
    assert np.all(result.edge_participation <= 1.0 + 1.0e-12)
    assert np.all(result.inverse_participation > 0.0)
