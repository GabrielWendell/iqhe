"""Independent interband-Kubo curvature and Chern-integration tests."""

import numpy as np

from qhe.models import (
    DiracParameters,
    bloch_hamiltonian_derivatives,
    HarperHofstadterParameters,
    massive_dirac_berry_curvature,
    massive_dirac_hamiltonian,
    massive_dirac_hamiltonian_derivatives,
)
from qhe.topology import (
    harper_hofstadter_band_mesh,
    interband_kubo_curvature_at_point,
    kubo_from_band_mesh,
)


def test_kubo_matches_analytic_massive_dirac_curvature() -> None:
    parameters = DiracParameters(v_fermi=1.2, mass=0.4)
    kx, ky = 0.21, -0.37
    energies, vectors = np.linalg.eigh(massive_dirac_hamiltonian(kx, ky, parameters))
    derivative_x, derivative_y = massive_dirac_hamiltonian_derivatives(parameters)

    numerical = interband_kubo_curvature_at_point(
        energies,
        vectors,
        derivative_x,
        derivative_y,
    )
    analytic = np.asarray(massive_dirac_berry_curvature(kx, ky, parameters))
    assert np.allclose(numerical, analytic, atol=1.0e-12, rtol=1.0e-12)


def test_kubo_harper_hofstadter_chern_numbers_converge_at_moderate_mesh() -> None:
    parameters = HarperHofstadterParameters(p=1, q=3)
    sampled = harper_hofstadter_band_mesh(parameters, nkx=41)
    result = kubo_from_band_mesh(
        sampled,
        lambda kx, ky: bloch_hamiltonian_derivatives(kx, ky, parameters),
    )

    assert np.allclose(result.chern_numbers, np.array([-1.0, 2.0, -1.0]), atol=1.0e-5)
    assert np.all(result.minimum_direct_gaps > 1.0)
