"""Wave-packet construction and edge-eigenstate projection for Stage 6 dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from qhe.boundary import BulkGap

EdgeSide = Literal["left", "right", "bottom", "top"]


@dataclass(frozen=True, slots=True)
class GaussianPacket:
    """Parameters defining a finite-lattice Gaussian seed state."""

    side: EdgeSide = "left"
    center_longitudinal: float = 0.5
    offset_from_boundary: float = 1.0
    sigma_transverse: float = 0.8
    sigma_longitudinal: float = 5.0
    momentum: float = 0.0

    def __post_init__(self) -> None:
        if self.side not in {"left", "right", "bottom", "top"}:
            raise ValueError("side must be 'left', 'right', 'bottom', or 'top'.")
        if self.sigma_transverse <= 0.0 or self.sigma_longitudinal <= 0.0:
            raise ValueError("Gaussian widths must be strictly positive.")
        if self.offset_from_boundary < 0.0:
            raise ValueError("offset_from_boundary must be non-negative.")


def normalize_state(state: np.ndarray, *, atol: float = 1.0e-14) -> np.ndarray:
    """Return a normalized complex state vector without modifying the input."""

    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1:
        raise ValueError("state must be one-dimensional.")
    norm = float(np.linalg.norm(vector))
    if norm <= atol:
        raise ValueError("Cannot normalize a zero or numerically null state.")
    return vector / norm


def _coordinates(lx: int, ly: int) -> tuple[np.ndarray, np.ndarray]:
    """Return flattened x/y coordinate arrays in the frozen lattice order."""

    if lx <= 0 or ly <= 0:
        raise ValueError("lx and ly must be strictly positive.")
    m = np.repeat(np.arange(int(lx), dtype=float), int(ly))
    n = np.tile(np.arange(int(ly), dtype=float), int(lx))
    return m, n


def gaussian_edge_seed(
    lx: int,
    ly: int,
    packet: GaussianPacket,
) -> np.ndarray:
    """Construct a normalized Gaussian seed near one finite-lattice boundary.

    For left/right edges the longitudinal coordinate is ``y`` and the phase factor is
    ``exp(i k_y y)``.  For bottom/top edges the longitudinal coordinate is ``x`` and the phase
    factor is ``exp(i k_x x)``.  The returned vector is not yet projected onto edge eigenstates.
    """

    m, n = _coordinates(int(lx), int(ly))
    if packet.side == "left":
        transverse = m
        longitudinal = n
        transverse_center = packet.offset_from_boundary
        longitudinal_center = packet.center_longitudinal * (int(ly) - 1)
    elif packet.side == "right":
        transverse = m
        longitudinal = n
        transverse_center = int(lx) - 1 - packet.offset_from_boundary
        longitudinal_center = packet.center_longitudinal * (int(ly) - 1)
    elif packet.side == "bottom":
        transverse = n
        longitudinal = m
        transverse_center = packet.offset_from_boundary
        longitudinal_center = packet.center_longitudinal * (int(lx) - 1)
    else:
        transverse = n
        longitudinal = m
        transverse_center = int(ly) - 1 - packet.offset_from_boundary
        longitudinal_center = packet.center_longitudinal * (int(lx) - 1)

    envelope = np.exp(
        -0.5 * ((transverse - transverse_center) / packet.sigma_transverse) ** 2
        - 0.5 * ((longitudinal - longitudinal_center) / packet.sigma_longitudinal) ** 2
    )
    phase = np.exp(1.0j * packet.momentum * longitudinal)
    return normalize_state(envelope.astype(np.complex128) * phase)


def edge_gap_selection(
    energies: np.ndarray,
    eigenvectors: np.ndarray,
    gap: BulkGap,
    side_mask: np.ndarray,
    *,
    minimum_side_participation: float = 0.20,
    energy_margin_fraction: float = 0.0,
) -> np.ndarray:
    """Select eigenstates in a bulk gap with non-negligible participation on one side."""

    values = np.asarray(energies, dtype=float)
    vectors = np.asarray(eigenvectors, dtype=np.complex128)
    mask = np.asarray(side_mask, dtype=bool)
    if values.ndim != 1 or vectors.ndim != 2:
        raise ValueError("energies must be one-dimensional and eigenvectors two-dimensional.")
    if vectors.shape != (values.size, values.size):
        raise ValueError("eigenvectors must be a square matrix whose columns match energies.")
    if mask.shape != (values.size,):
        raise ValueError("side_mask length must match the eigenvector dimension.")
    if not 0.0 <= minimum_side_participation <= 1.0:
        raise ValueError("minimum_side_participation must lie in [0, 1].")
    if energy_margin_fraction < 0.0 or energy_margin_fraction >= 0.5:
        raise ValueError("energy_margin_fraction must lie in [0, 0.5).")

    margin = energy_margin_fraction * gap.width
    in_gap = (values > gap.lower_edge + margin) & (values < gap.upper_edge - margin)
    density = np.abs(vectors) ** 2
    side_participation = np.sum(density[mask, :], axis=0)
    selected = in_gap & (side_participation >= minimum_side_participation)
    if not np.any(selected):
        raise ValueError(
            "No edge eigenstates satisfy the gap and side-participation criteria; "
            "try a larger system or a lower threshold."
        )
    return selected


def project_onto_subspace(
    seed: np.ndarray,
    eigenvectors: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Project ``seed`` onto the column space of ``eigenvectors`` while preserving phases."""

    vector = normalize_state(seed)
    basis = np.asarray(eigenvectors, dtype=np.complex128)
    if basis.ndim != 2 or basis.shape[0] != vector.size:
        raise ValueError("eigenvectors must have shape (n_sites, n_selected).")
    if basis.shape[1] == 0:
        raise ValueError("Cannot project onto an empty subspace.")
    coefficients = basis.conj().T @ vector
    projected = basis @ coefficients
    return normalize_state(projected), coefficients


__all__ = [
    "EdgeSide",
    "GaussianPacket",
    "edge_gap_selection",
    "gaussian_edge_seed",
    "normalize_state",
    "project_onto_subspace",
]
