"""Time-domain edge-retention, leakage, centroid, and velocity observables."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qhe.dynamics.packets import EdgeSide


@dataclass(frozen=True, slots=True)
class VelocityFit:
    """Linear fit of a packet coordinate as a function of time."""

    velocity: float
    intercept: float
    rms_residual: float
    time_min: float
    time_max: float


def probability_timeseries(states: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Return probability contained in ``mask`` at each time."""

    array = np.asarray(states, dtype=np.complex128)
    resolved_mask = np.asarray(mask, dtype=bool)
    if array.ndim != 2:
        raise ValueError("states must have shape (n_times, n_sites).")
    if resolved_mask.shape != (array.shape[1],):
        raise ValueError("mask length must match the number of lattice sites.")
    return np.sum(np.abs(array[:, resolved_mask]) ** 2, axis=1)


def bulk_leakage(edge_probability: np.ndarray) -> np.ndarray:
    """Return bulk leakage as ``1 - P_edge``."""

    values = np.asarray(edge_probability, dtype=float)
    if values.ndim != 1:
        raise ValueError("edge_probability must be one-dimensional.")
    return 1.0 - values


def coordinate_arrays(lx: int, ly: int) -> tuple[np.ndarray, np.ndarray]:
    """Return flattened x/y coordinate arrays in the frozen lattice order."""

    if lx <= 0 or ly <= 0:
        raise ValueError("lx and ly must be strictly positive.")
    x = np.repeat(np.arange(int(lx), dtype=float), int(ly))
    y = np.tile(np.arange(int(ly), dtype=float), int(lx))
    return x, y


def centroid_timeseries(
    states: np.ndarray,
    lx: int,
    ly: int,
    *,
    mask: np.ndarray | None = None,
    atol: float = 1.0e-14,
) -> tuple[np.ndarray, np.ndarray]:
    """Return masked centroid coordinates at each time."""

    array = np.asarray(states, dtype=np.complex128)
    if array.ndim != 2:
        raise ValueError("states must have shape (n_times, n_sites).")
    x, y = coordinate_arrays(int(lx), int(ly))
    if array.shape[1] != x.size:
        raise ValueError("states are incompatible with lx and ly.")
    if mask is None:
        resolved_mask = np.ones(x.size, dtype=bool)
    else:
        resolved_mask = np.asarray(mask, dtype=bool)
        if resolved_mask.shape != (x.size,):
            raise ValueError("mask length must equal lx * ly.")
    density = np.abs(array[:, resolved_mask]) ** 2
    mass = np.sum(density, axis=1)
    if np.any(mass <= atol):
        raise ValueError("Masked probability is zero at one or more times.")
    centroid_x = density @ x[resolved_mask] / mass
    centroid_y = density @ y[resolved_mask] / mass
    return centroid_x, centroid_y


def edge_coordinate_timeseries(
    states: np.ndarray,
    lx: int,
    ly: int,
    side: EdgeSide,
    mask: np.ndarray,
) -> np.ndarray:
    """Return a side-adapted longitudinal coordinate for an edge packet."""

    centroid_x, centroid_y = centroid_timeseries(states, lx, ly, mask=mask)
    if side in {"left", "right"}:
        return centroid_y
    return centroid_x


def estimate_velocity(
    times: np.ndarray,
    coordinate: np.ndarray,
    *,
    fit_until: float | None = None,
) -> VelocityFit:
    """Estimate packet velocity by fitting a coordinate to a straight line."""

    resolved_times = np.asarray(times, dtype=float)
    values = np.asarray(coordinate, dtype=float)
    if resolved_times.ndim != 1 or values.ndim != 1 or resolved_times.size != values.size:
        raise ValueError("times and coordinate must be one-dimensional arrays of equal length.")
    if resolved_times.size < 3:
        raise ValueError("At least three time samples are required for a velocity fit.")
    if fit_until is None:
        mask = np.ones(resolved_times.size, dtype=bool)
    else:
        mask = resolved_times <= float(fit_until)
    if np.count_nonzero(mask) < 3:
        raise ValueError("Velocity fit window contains fewer than three samples.")
    velocity, intercept = np.polyfit(resolved_times[mask], values[mask], deg=1)
    residual = values[mask] - (velocity * resolved_times[mask] + intercept)
    return VelocityFit(
        velocity=float(velocity),
        intercept=float(intercept),
        rms_residual=float(np.sqrt(np.mean(residual**2))),
        time_min=float(np.min(resolved_times[mask])),
        time_max=float(np.max(resolved_times[mask])),
    )


__all__ = [
    "VelocityFit",
    "bulk_leakage",
    "centroid_timeseries",
    "coordinate_arrays",
    "edge_coordinate_timeseries",
    "estimate_velocity",
    "probability_timeseries",
]
