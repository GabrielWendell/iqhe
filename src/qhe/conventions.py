r"""Frozen physical and numerical conventions for the QHE-EJP project.

Stage 1 turns these conventions into a single importable source of truth.  Numerical
modules must use this information rather than silently introducing independent signs,
gauges, units, or indexing choices.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FrozenConventions:
    """Project-wide conventions adopted in Stage 1.

    The scalar ``elementary_charge`` is positive by definition.  The electron charge is
    therefore ``electron_charge = -elementary_charge``.  The natural-unit convention
    uses :math:`\\hbar = 1` and lattice spacing :math:`a = 1` unless a model parameter
    explicitly overrides the lattice spacing.
    """

    elementary_charge: float = 1.0
    electron_charge: float = -1.0
    hbar: float = 1.0
    lattice_spacing: float = 1.0
    magnetic_field_direction: str = "+z"
    gauge: str = "Landau gauge A = (0, Bx, 0)"
    berry_connection: str = "A_n,mu = i <u_n | partial_{k_mu} u_n>"
    berry_curvature: str = "Omega_n = partial_kx A_n,y - partial_ky A_n,x"
    chern_number: str = "C_n = (1 / 2pi) integral_BZ Omega_n d^2k"
    hall_conductivity: str = "sigma_xy = -(e^2 / h) sum_{n in occ} C_n"
    site_indexing: str = "index(m, n; Ly) = m * Ly + n; reshape -> (Lx, Ly)"
    fhs_orientation: str = (
        "Use -Arg[U_x(k) U_y(k+x) U_x(k+y)^(-1) U_y(k)^(-1)] so that "
        "the discrete result matches the Berry convention above."
    )

    @property
    def flux_quantum(self) -> float:
        """Flux quantum ``Phi_0 = h / e = 2 pi hbar / e`` in chosen units."""

        return 2.0 * 3.141592653589793 * self.hbar / self.elementary_charge


CONVENTIONS = FrozenConventions()


__all__ = ["CONVENTIONS", "FrozenConventions"]
