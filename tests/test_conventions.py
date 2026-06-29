"""Tests that freeze the Stage-1 convention source of truth."""

import numpy as np

from qhe.conventions import CONVENTIONS


def test_stage1_units_and_charge_conventions_are_frozen() -> None:
    assert CONVENTIONS.elementary_charge == 1.0
    assert CONVENTIONS.electron_charge == -1.0
    assert CONVENTIONS.hbar == 1.0
    assert CONVENTIONS.lattice_spacing == 1.0
    assert np.isclose(CONVENTIONS.flux_quantum, 2.0 * np.pi)


def test_stage1_convention_text_records_fhs_orientation() -> None:
    assert 'Use -Arg' in CONVENTIONS.fhs_orientation
    assert 'sigma_xy' in CONVENTIONS.hall_conductivity
