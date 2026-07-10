"""Local bond-current diagnostics for the Harper-Hofstadter model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qhe.dynamics.packets import EdgeSide
from qhe.models import HarperHofstadterParameters, peierls_phase, site_index


@dataclass(frozen=True, slots=True)
class BondCurrents:
    """Forward nearest-neighbour bond currents for a finite open lattice."""

    jx: np.ndarray
    jy: np.ndarray

    @property
    def max_abs(self) -> float:
        return float(max(np.max(np.abs(self.jx)), np.max(np.abs(self.jy))))


def bond_currents(
    state: np.ndarray,
    lx: int,
    ly: int,
    parameters: HarperHofstadterParameters | None = None,
    *,
    hbar: float = 1.0,
) -> BondCurrents:
    """Compute forward-x and forward-y bond currents for one normalized state.

    The sign convention follows the manuscript diagnostic
    ``J_{i->j} = (2/hbar) Im[t_ij exp(i theta_ij) psi_i^* psi_j]`` with positive hopping
    amplitudes ``t_x`` and ``t_y``.  The y bonds carry the frozen Landau-gauge Peierls phase.
    """

    if hbar <= 0.0:
        raise ValueError("hbar must be strictly positive.")
    params = parameters or HarperHofstadterParameters()
    psi = np.asarray(state, dtype=np.complex128)
    if psi.shape != (int(lx) * int(ly),):
        raise ValueError("state length must equal lx * ly.")
    jx = np.zeros((int(lx) - 1, int(ly)), dtype=float)
    jy = np.zeros((int(lx), int(ly) - 1), dtype=float)
    for m in range(int(lx)):
        for n in range(int(ly)):
            origin = site_index(m, n, int(ly))
            if m + 1 < int(lx):
                target = site_index(m + 1, n, int(ly))
                jx[m, n] = (2.0 / hbar) * np.imag(
                    params.tx * np.conjugate(psi[origin]) * psi[target]
                )
            if n + 1 < int(ly):
                target = site_index(m, n + 1, int(ly))
                jy[m, n] = (2.0 / hbar) * np.imag(
                    params.ty * peierls_phase(m, params) * np.conjugate(psi[origin]) * psi[target]
                )
    return BondCurrents(jx=jx, jy=jy)


def side_current_indicator(
    currents: BondCurrents,
    side: EdgeSide,
    *,
    edge_width: int,
) -> float:
    """Return a signed mean current along the selected boundary strip."""

    if edge_width <= 0:
        raise ValueError("edge_width must be strictly positive.")
    if side == "left":
        return float(np.mean(currents.jy[:edge_width, :]))
    if side == "right":
        return float(np.mean(currents.jy[-edge_width:, :]))
    if side == "bottom":
        return float(np.mean(currents.jx[:, :edge_width]))
    if side == "top":
        return float(np.mean(currents.jx[:, -edge_width:]))
    raise ValueError("side must be 'left', 'right', 'bottom', or 'top'.")


__all__ = ["BondCurrents", "bond_currents", "side_current_indicator"]
