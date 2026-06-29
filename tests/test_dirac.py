"""Regression tests for the massive Dirac warm-up Hamiltonian."""

import numpy as np

from qhe.models import DiracParameters, massive_dirac_energies, massive_dirac_hamiltonian
from qhe.validation import assert_hermitian


def test_massive_dirac_hamiltonian_is_hermitian() -> None:
    matrix = massive_dirac_hamiltonian(0.2, -0.7, DiracParameters(v_fermi=1.5, mass=0.25))
    assert_hermitian(matrix)


def test_massive_dirac_eigenvalues_match_analytic_spectrum() -> None:
    params = DiracParameters(v_fermi=1.7, mass=-0.4)
    numeric = np.linalg.eigvalsh(massive_dirac_hamiltonian(0.3, -0.2, params))
    analytic = np.asarray(massive_dirac_energies(0.3, -0.2, params))
    assert np.allclose(numeric, analytic, atol=1e-12)
