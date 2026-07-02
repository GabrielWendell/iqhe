"""Unit tests for reusable edge-strip geometry and localization metrics."""

import numpy as np
import pytest

from qhe.boundary import (
    inverse_participation_ratio,
    open_edge_mask,
    probability_mass,
    ribbon_edge_masks,
)


def test_ribbon_edge_masks_are_disjoint_and_cover_requested_width() -> None:
    masks = ribbon_edge_masks(12, 3)
    assert masks.left.sum() == 3
    assert masks.right.sum() == 3
    assert masks.total.sum() == 6
    assert not np.any(masks.left & masks.right)


def test_ribbon_edge_masks_reject_overlap() -> None:
    with pytest.raises(ValueError, match="overlapping"):
        ribbon_edge_masks(5, 3)


def test_open_edge_mask_follows_row_major_site_convention() -> None:
    edge = open_edge_mask(6, 8, 2)
    grid = edge.mask.reshape(6, 8)
    assert grid[:2, :].all()
    assert grid[-2:, :].all()
    assert grid[:, :2].all()
    assert grid[:, -2:].all()
    assert not grid[3, 3]


def test_probability_mass_and_ipr_handle_state_columns() -> None:
    masks = ribbon_edge_masks(8, 2)
    states = np.zeros((8, 2), dtype=np.complex128)
    states[0, 0] = 1.0
    states[:, 1] = 1.0 / np.sqrt(8.0)
    edge_mass = probability_mass(states, masks.total)
    assert np.allclose(edge_mass, [1.0, 0.5])
    assert np.allclose(inverse_participation_ratio(states), [1.0, 1.0 / 8.0])
