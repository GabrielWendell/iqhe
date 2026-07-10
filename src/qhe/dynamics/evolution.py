"""Unitary spectral time evolution and norm diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qhe.dynamics.packets import normalize_state
from qhe.validation import assert_hermitian


@dataclass(frozen=True, slots=True)
class SpectralDecomposition:
    """Eigen-decomposition of a finite Hermitian Hamiltonian."""

    energies: np.ndarray
    eigenvectors: np.ndarray

    def __post_init__(self) -> None:
        if self.energies.ndim != 1 or self.eigenvectors.ndim != 2:
            raise ValueError("Invalid spectral decomposition dimensions.")
        if self.eigenvectors.shape != (self.energies.size, self.energies.size):
            raise ValueError("Eigenvectors must be a square column matrix matching energies.")


@dataclass(frozen=True, slots=True)
class NormDiagnostics:
    """Time-series norm-conservation diagnostics."""

    norms: np.ndarray

    @property
    def max_deviation(self) -> float:
        return float(np.max(np.abs(self.norms - 1.0)))

    @property
    def min_norm(self) -> float:
        return float(np.min(self.norms))

    @property
    def max_norm(self) -> float:
        return float(np.max(self.norms))


def diagonalize_hamiltonian(hamiltonian: np.ndarray) -> SpectralDecomposition:
    """Diagonalize a Hermitian finite Hamiltonian for later unitary propagation."""

    matrix = np.asarray(hamiltonian, dtype=np.complex128)
    assert_hermitian(matrix)
    energies, eigenvectors = np.linalg.eigh(matrix)
    return SpectralDecomposition(energies=energies, eigenvectors=eigenvectors)


def evolve_spectral(
    decomposition: SpectralDecomposition,
    initial_state: np.ndarray,
    times: np.ndarray,
    *,
    hbar: float = 1.0,
) -> np.ndarray:
    """Evolve a state under a time-independent Hamiltonian without renormalization."""

    if hbar <= 0.0:
        raise ValueError("hbar must be strictly positive.")
    resolved_times = np.asarray(times, dtype=float)
    if resolved_times.ndim != 1 or resolved_times.size == 0:
        raise ValueError("times must be a non-empty one-dimensional array.")
    psi0 = normalize_state(initial_state)
    if psi0.size != decomposition.energies.size:
        raise ValueError("Initial-state dimension is incompatible with the decomposition.")
    coefficients = decomposition.eigenvectors.conj().T @ psi0
    phases = np.exp(-1.0j * np.outer(resolved_times, decomposition.energies) / hbar)
    return (phases * coefficients[None, :]) @ decomposition.eigenvectors.T


def norm_diagnostics(states: np.ndarray) -> NormDiagnostics:
    """Return norm diagnostics for one state at each sampled time."""

    array = np.asarray(states, dtype=np.complex128)
    if array.ndim != 2:
        raise ValueError("states must have shape (n_times, n_sites).")
    return NormDiagnostics(norms=np.sum(np.abs(array) ** 2, axis=1))


__all__ = [
    "NormDiagnostics",
    "SpectralDecomposition",
    "diagonalize_hamiltonian",
    "evolve_spectral",
    "norm_diagnostics",
]
