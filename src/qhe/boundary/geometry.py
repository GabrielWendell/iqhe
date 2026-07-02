"""Geometry-aware probability and localization metrics for finite QHE lattices.

The Stage-3 edge analysis deliberately keeps the geometry layer separate from spectrum
construction.  This makes the definition of an ``edge strip`` explicit and reusable for both
cylindrical ribbons and fully open finite lattices.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class RibbonEdgeMasks:
    """Boolean masks for the two disjoint x edges of an x-open ribbon."""

    left: np.ndarray
    right: np.ndarray
    total: np.ndarray
    width: int

    def __post_init__(self) -> None:
        if self.left.ndim != 1 or self.right.ndim != 1 or self.total.ndim != 1:
            raise ValueError("Ribbon edge masks must be one-dimensional.")
        if self.left.shape != self.right.shape or self.left.shape != self.total.shape:
            raise ValueError("Ribbon edge masks must have matching shapes.")
        if self.width <= 0:
            raise ValueError("Ribbon edge width must be strictly positive.")
        if np.any(self.left & self.right):
            raise ValueError("Left and right ribbon masks must be disjoint.")
        if not np.array_equal(self.total, self.left | self.right):
            raise ValueError("Ribbon total mask must be the union of left and right masks.")

    @property
    def n_sites(self) -> int:
        """Number of transverse ribbon sites."""

        return int(self.total.size)


@dataclass(frozen=True, slots=True)
class OpenEdgeMask:
    """Boolean perimeter-strip mask for a fully open rectangular lattice."""

    mask: np.ndarray
    lx: int
    ly: int
    width: int

    def __post_init__(self) -> None:
        if self.mask.shape != (self.lx * self.ly,):
            raise ValueError("Open edge mask shape must equal (lx * ly,).")
        if self.lx <= 0 or self.ly <= 0 or self.width <= 0:
            raise ValueError("Open mask dimensions and width must be strictly positive.")


def _validate_edge_width(length: int, width: int, *, name: str) -> None:
    if length <= 0:
        raise ValueError(f"{name} must be strictly positive.")
    if width <= 0:
        raise ValueError("edge_width must be strictly positive.")
    if 2 * width > length:
        raise ValueError(
            "edge_width creates overlapping opposite-edge strips; require 2 * edge_width <= "
            f"{name}."
        )


def ribbon_edge_masks(lx: int, edge_width: int) -> RibbonEdgeMasks:
    """Return disjoint left/right edge strips for an x-open ribbon.

    The ribbon basis is ordered by the x coordinate, so a ribbon eigenvector has length ``lx``.
    The returned total mask is the union of the two disjoint strips.
    """

    _validate_edge_width(int(lx), int(edge_width), name="lx")
    left = np.zeros(int(lx), dtype=bool)
    right = np.zeros(int(lx), dtype=bool)
    left[: int(edge_width)] = True
    right[int(lx) - int(edge_width) :] = True
    return RibbonEdgeMasks(left=left, right=right, total=left | right, width=int(edge_width))


def open_edge_mask(lx: int, ly: int, edge_width: int) -> OpenEdgeMask:
    """Return a flattened perimeter-strip mask for a fully open ``(lx, ly)`` lattice.

    The flattening follows the frozen Stage-1 state-vector convention
    ``index(m, n; Ly) = m * Ly + n``.  The width is constrained to keep opposite strips
    disjoint in both lattice directions, which makes edge fractions interpretable.
    """

    _validate_edge_width(int(lx), int(edge_width), name="lx")
    _validate_edge_width(int(ly), int(edge_width), name="ly")
    m = np.arange(int(lx))[:, None]
    n = np.arange(int(ly))[None, :]
    grid = (
        (m < edge_width)
        | (m >= lx - edge_width)
        | (n < edge_width)
        | (n >= ly - edge_width)
    )
    return OpenEdgeMask(mask=grid.reshape(lx * ly), lx=int(lx), ly=int(ly), width=int(edge_width))


def _as_state_matrix(states: np.ndarray, n_sites: int) -> tuple[np.ndarray, bool]:
    """Return state columns with shape ``(n_sites, n_states)`` and a scalar-input marker."""

    array = np.asarray(states, dtype=np.complex128)
    if array.ndim == 1:
        if array.shape[0] != n_sites:
            raise ValueError("State length does not match mask length.")
        return array[:, None], True
    if array.ndim == 2:
        if array.shape[0] != n_sites:
            raise ValueError("State matrix first dimension does not match mask length.")
        return array, False
    raise ValueError(
        "states must be a one-dimensional state or a two-dimensional state-column matrix."
    )


def probability_mass(
    states: np.ndarray,
    mask: np.ndarray,
    *,
    normalize: bool = True,
    atol: float = 1.0e-14,
) -> float | np.ndarray:
    """Return probability contained in a Boolean mask for one or several state columns.

    When ``normalize=True`` (the default), the result is divided by each state norm.  This is
    convenient for diagnostics because it keeps participation interpretable even before an
    upstream normalization assertion is applied.
    """

    resolved_mask = np.asarray(mask, dtype=bool)
    if resolved_mask.ndim != 1:
        raise ValueError("mask must be one-dimensional.")
    matrix, was_vector = _as_state_matrix(states, resolved_mask.size)
    density = np.abs(matrix) ** 2
    numerator = np.sum(density[resolved_mask, :], axis=0)
    if normalize:
        denominator = np.sum(density, axis=0)
        if np.any(denominator <= atol):
            raise ValueError("Cannot normalize a state with zero or numerically null norm.")
        result = numerator / denominator
    else:
        result = numerator
    return float(result[0]) if was_vector else np.asarray(result, dtype=float)


def inverse_participation_ratio(
    states: np.ndarray,
    *,
    normalize: bool = True,
    atol: float = 1.0e-14,
) -> float | np.ndarray:
    """Return ``sum_i |psi_i|^4`` for normalized one or several state columns.

    For a normalized state extended uniformly over ``N`` sites, the IPR is approximately
    ``1 / N``; for a single-site state it equals one.
    """

    array = np.asarray(states, dtype=np.complex128)
    if array.ndim == 1:
        matrix = array[:, None]
        was_vector = True
    elif array.ndim == 2:
        matrix = array
        was_vector = False
    else:
        raise ValueError(
        "states must be a one-dimensional state or a two-dimensional state-column matrix."
    )

    density = np.abs(matrix) ** 2
    if normalize:
        norm = np.sum(density, axis=0)
        if np.any(norm <= atol):
            raise ValueError("Cannot normalize a state with zero or numerically null norm.")
        density = density / norm
    result = np.sum(density**2, axis=0)
    return float(result[0]) if was_vector else np.asarray(result, dtype=float)


__all__ = [
    "OpenEdgeMask",
    "RibbonEdgeMasks",
    "inverse_participation_ratio",
    "open_edge_mask",
    "probability_mass",
    "ribbon_edge_masks",
]
