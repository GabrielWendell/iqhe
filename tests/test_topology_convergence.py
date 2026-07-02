"""End-to-end Stage-2 convergence tests for the canonical Hofstadter model."""

import numpy as np

from qhe.models import HarperHofstadterParameters
from qhe.topology import harper_hofstadter_convergence


def test_fhs_kubo_residuals_decrease_under_mesh_refinement() -> None:
    result = harper_hofstadter_convergence(
        HarperHofstadterParameters(p=1, q=3),
        mesh_sizes=(11, 21, 41),
    )

    expected = np.array([-1.0, 2.0, -1.0])
    assert np.allclose(result.fhs_chern_numbers, expected, atol=1.0e-10)
    assert np.allclose(result.kubo_chern_numbers[-1], expected, atol=1.0e-5)
    assert np.all(result.minimum_direct_gaps > 1.0)
    assert np.all(result.l2_errors[-1] < result.l2_errors[0])
    assert np.all(result.linf_errors[-1] < result.linf_errors[0])
