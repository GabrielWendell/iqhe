"""Controlled boundary defects for finite open Harper-Hofstadter systems."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qhe.dynamics.packets import EdgeSide
from qhe.models import site_index
from qhe.validation import assert_hermitian


@dataclass(frozen=True, slots=True)
class WeakLinkDefect:
    """A single weakened nearest-neighbour boundary link."""

    side: EdgeSide
    position: int
    factor: float = 0.0

    def __post_init__(self) -> None:
        if self.side not in {"left", "right", "bottom", "top"}:
            raise ValueError("side must be 'left', 'right', 'bottom', or 'top'.")
        if self.position < 0:
            raise ValueError("position must be non-negative.")
        if not 0.0 <= self.factor <= 1.0:
            raise ValueError("factor must lie in [0, 1].")


def boundary_link_sites(lx: int, ly: int, defect: WeakLinkDefect) -> tuple[int, int]:
    """Return flattened endpoint indices for a boundary weak-link defect."""

    if lx <= 1 or ly <= 1:
        raise ValueError("lx and ly must both be greater than one.")
    if defect.side == "left":
        if defect.position >= ly - 1:
            raise ValueError("left/right weak-link position must be less than ly - 1.")
        return site_index(0, defect.position, ly), site_index(0, defect.position + 1, ly)
    if defect.side == "right":
        if defect.position >= ly - 1:
            raise ValueError("left/right weak-link position must be less than ly - 1.")
        return site_index(lx - 1, defect.position, ly), site_index(lx - 1, defect.position + 1, ly)
    if defect.side == "bottom":
        if defect.position >= lx - 1:
            raise ValueError("bottom/top weak-link position must be less than lx - 1.")
        return site_index(defect.position, 0, ly), site_index(defect.position + 1, 0, ly)
    if defect.position >= lx - 1:
        raise ValueError("bottom/top weak-link position must be less than lx - 1.")
    return site_index(defect.position, ly - 1, ly), site_index(defect.position + 1, ly - 1, ly)


def apply_weak_link_defect(
    hamiltonian: np.ndarray,
    lx: int,
    ly: int,
    defect: WeakLinkDefect,
) -> np.ndarray:
    """Return a copy of ``hamiltonian`` with one boundary link multiplied by ``factor``."""

    matrix = np.array(hamiltonian, dtype=np.complex128, copy=True)
    if matrix.shape != (int(lx) * int(ly), int(lx) * int(ly)):
        raise ValueError("Hamiltonian shape must equal (lx * ly, lx * ly).")
    first, second = boundary_link_sites(int(lx), int(ly), defect)
    matrix[first, second] *= defect.factor
    matrix[second, first] = np.conjugate(matrix[first, second])
    assert_hermitian(matrix)
    return matrix


__all__ = ["WeakLinkDefect", "apply_weak_link_defect", "boundary_link_sites"]
