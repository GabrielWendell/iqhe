"""Tests for Stage-6 finite-lattice side masks."""

from __future__ import annotations

import numpy as np

from qhe.boundary import open_side_masks


def test_open_side_masks_have_expected_union_and_corners() -> None:
    masks = open_side_masks(6, 8, 2)
    assert masks.left.shape == (48,)
    assert masks.right.shape == (48,)
    assert masks.bottom.shape == (48,)
    assert masks.top.shape == (48,)
    assert np.array_equal(masks.perimeter, masks.left | masks.right | masks.bottom | masks.top)
    assert np.any(masks.left & masks.bottom)
    assert np.count_nonzero(masks.left) == 2 * 8
    assert np.count_nonzero(masks.top) == 6 * 2


def test_open_side_masks_reject_unknown_side() -> None:
    masks = open_side_masks(6, 8, 2)
    try:
        masks.side("diagonal")
    except ValueError as exc:
        assert "side must be" in str(exc)
    else:  # pragma: no cover - defensive branch
        raise AssertionError("unknown side should have raised ValueError")
