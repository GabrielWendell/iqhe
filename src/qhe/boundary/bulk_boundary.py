"""Quantitative finite-ribbon diagnostics for bulk-boundary correspondence.

This module does not attempt to prove the bulk-boundary theorem numerically.  Instead, it makes
its finite-system signature measurable: given bulk Chern data and a ribbon spectrum, it identifies
edge-localized crossings of a reference energy inside every global bulk gap and reports their
orientation separately on the left and right boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from qhe.boundary.ribbon import RibbonSpectrum, diagonalize_ribbon
from qhe.models import HarperHofstadterParameters
from qhe.topology import BandMesh, TopologyAnalysis, analyze_harper_hofstadter_topology


@dataclass(frozen=True, slots=True)
class BulkGap:
    """Global energy gap between two adjacent periodic bulk bands."""

    index: int
    lower_edge: float
    upper_edge: float
    gap_chern_number: int

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("Gap index must be non-negative.")
        if not self.upper_edge > self.lower_edge:
            raise ValueError("A bulk gap must have strictly positive width.")

    @property
    def width(self) -> float:
        return float(self.upper_edge - self.lower_edge)

    @property
    def reference_energy(self) -> float:
        return float(0.5 * (self.lower_edge + self.upper_edge))


@dataclass(frozen=True, slots=True)
class EdgeCrossing:
    """An edge-localized ribbon-band crossing of a chosen reference energy."""

    band_index: int
    segment_index: int
    ky: float
    energy: float
    slope: float
    left_participation: float
    right_participation: float
    edge_participation: float
    side: str

    def __post_init__(self) -> None:
        if self.band_index < 0 or self.segment_index < 0:
            raise ValueError("Band and segment indices must be non-negative.")
        if self.side not in {"left", "right", "ambiguous"}:
            raise ValueError("side must be 'left', 'right', or 'ambiguous'.")
        if self.edge_participation < 0.0 or self.edge_participation > 1.0 + 1.0e-12:
            raise ValueError("edge_participation must lie in [0, 1].")

    @property
    def orientation(self) -> int:
        """Return the crossing orientation, ``sign(dE/dky)``."""

        return int(np.sign(self.slope))


@dataclass(frozen=True, slots=True)
class GapCrossingSummary:
    """Side-resolved finite-ribbon crossing record for one bulk energy gap."""

    gap: BulkGap
    crossings: tuple[EdgeCrossing, ...]

    @property
    def left_crossings(self) -> tuple[EdgeCrossing, ...]:
        return tuple(crossing for crossing in self.crossings if crossing.side == "left")

    @property
    def right_crossings(self) -> tuple[EdgeCrossing, ...]:
        return tuple(crossing for crossing in self.crossings if crossing.side == "right")

    @property
    def ambiguous_crossings(self) -> tuple[EdgeCrossing, ...]:
        return tuple(crossing for crossing in self.crossings if crossing.side == "ambiguous")

    @staticmethod
    def _oriented_count(crossings: Iterable[EdgeCrossing]) -> int:
        return int(sum(crossing.orientation for crossing in crossings))

    @property
    def left_oriented_crossing_count(self) -> int:
        """Signed number of reference-energy crossings on the left edge."""

        return self._oriented_count(self.left_crossings)

    @property
    def right_oriented_crossing_count(self) -> int:
        """Signed number of reference-energy crossings on the right edge."""

        return self._oriented_count(self.right_crossings)


@dataclass(frozen=True, slots=True)
class BulkBoundaryAnalysis:
    """Stage-3 joint record of bulk Chern data, global gaps, and ribbon crossings."""

    topology: TopologyAnalysis
    ribbon: RibbonSpectrum
    gaps: tuple[BulkGap, ...]
    crossing_summaries: tuple[GapCrossingSummary, ...]

    def __post_init__(self) -> None:
        if len(self.gaps) != len(self.crossing_summaries):
            raise ValueError("Each bulk gap must have exactly one crossing summary.")
        for gap, summary in zip(self.gaps, self.crossing_summaries, strict=True):
            if gap != summary.gap:
                raise ValueError("Crossing summaries must retain their corresponding bulk gap.")


def gap_chern_numbers(chern_numbers: np.ndarray) -> np.ndarray:
    """Return cumulative Chern numbers below each adjacent-band gap."""

    values = np.asarray(chern_numbers, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("chern_numbers must contain at least two one-dimensional band values.")
    rounded = np.rint(values).astype(int)
    if not np.allclose(values, rounded, atol=1.0e-8):
        raise ValueError(
            "Gap Chern numbers require numerically quantized integer band Chern values."
        )
    return np.cumsum(rounded)[:-1]


def bulk_gaps_from_band_mesh(
    band_mesh: BandMesh,
    chern_numbers: np.ndarray,
    *,
    positive_gap_floor: float = 1.0e-12,
) -> tuple[BulkGap, ...]:
    """Compute global adjacent-band gap intervals from a periodic Bloch mesh."""

    energies = np.asarray(band_mesh.energies, dtype=float)
    if energies.ndim != 3:
        raise ValueError("Band mesh energies must have shape (N_kx, N_ky, N_band).")
    cumulative = gap_chern_numbers(chern_numbers)
    if cumulative.size != energies.shape[-1] - 1:
        raise ValueError("Chern-number count is incompatible with the number of bulk bands.")

    gaps: list[BulkGap] = []
    for index in range(energies.shape[-1] - 1):
        lower = float(np.max(energies[..., index]))
        upper = float(np.min(energies[..., index + 1]))
        if upper - lower <= positive_gap_floor:
            raise ValueError(
                "Bulk gap "
                f"{index} is not positive on the supplied mesh: upper-lower={upper-lower:.3e}."
            )
        gaps.append(
            BulkGap(
                index=index,
                lower_edge=lower,
                upper_edge=upper,
                gap_chern_number=int(cumulative[index]),
            )
        )
    return tuple(gaps)


def _crosses_reference(first: float, second: float, reference: float) -> bool:
    """Return true for a strict sign change across a finite energy interval."""

    return (first - reference) * (second - reference) < 0.0


def _segment_spacing(ribbon: RibbonSpectrum, segment_index: int) -> float:
    """Return positive ky spacing, including the periodic final-to-first segment."""

    if segment_index < ribbon.nky - 1:
        return float(ribbon.ky[segment_index + 1] - ribbon.ky[segment_index])
    return float(
        (ribbon.ky[0] + 2.0 * np.pi / ribbon.parameters.lattice_spacing) - ribbon.ky[-1]
    )


def _interpolate_periodic_ky(ribbon: RibbonSpectrum, segment_index: int, fraction: float) -> float:
    """Linearly interpolate ky on one closed-open periodic segment."""

    first = float(ribbon.ky[segment_index])
    if segment_index < ribbon.nky - 1:
        second = float(ribbon.ky[segment_index + 1])
    else:
        second = float(ribbon.ky[0] + 2.0 * np.pi / ribbon.parameters.lattice_spacing)
    value = first + fraction * (second - first)
    upper = np.pi / ribbon.parameters.lattice_spacing
    lower = -upper
    if value >= upper:
        value -= 2.0 * upper
    if value < lower:
        value += 2.0 * upper
    return float(value)


def find_edge_crossings(
    ribbon: RibbonSpectrum,
    gap: BulkGap,
    *,
    edge_threshold: float = 0.5,
    side_margin: float = 1.0e-3,
) -> tuple[EdgeCrossing, ...]:
    """Find edge-localized reference-energy crossings within one finite-ribbon bulk gap.

    A crossing is accepted only when the linearly interpolated state has total edge participation
    at least ``edge_threshold``.  Side assignment is based on the larger of left/right
    participation; nearly balanced states are labelled ``ambiguous`` rather than forced onto one
    boundary.
    """

    if not 0.0 < edge_threshold <= 1.0:
        raise ValueError("edge_threshold must lie in (0, 1].")
    if side_margin < 0.0:
        raise ValueError("side_margin must be non-negative.")

    crossings: list[EdgeCrossing] = []
    reference = gap.reference_energy
    for band_index in range(ribbon.lx):
        for segment_index in range(ribbon.nky):
            next_index = (segment_index + 1) % ribbon.nky
            first_energy = float(ribbon.energies[segment_index, band_index])
            second_energy = float(ribbon.energies[next_index, band_index])
            if not _crosses_reference(first_energy, second_energy, reference):
                continue

            fraction = (reference - first_energy) / (second_energy - first_energy)
            left = float(
                (1.0 - fraction) * ribbon.left_participation[segment_index, band_index]
                + fraction * ribbon.left_participation[next_index, band_index]
            )
            right = float(
                (1.0 - fraction) * ribbon.right_participation[segment_index, band_index]
                + fraction * ribbon.right_participation[next_index, band_index]
            )
            edge = left + right
            if edge < edge_threshold:
                continue

            if left - right > side_margin:
                side = "left"
            elif right - left > side_margin:
                side = "right"
            else:
                side = "ambiguous"
            slope = (second_energy - first_energy) / _segment_spacing(ribbon, segment_index)
            crossings.append(
                EdgeCrossing(
                    band_index=band_index,
                    segment_index=segment_index,
                    ky=_interpolate_periodic_ky(ribbon, segment_index, fraction),
                    energy=reference,
                    slope=float(slope),
                    left_participation=left,
                    right_participation=right,
                    edge_participation=edge,
                    side=side,
                )
            )
    return tuple(crossings)


def analyze_bulk_boundary_correspondence(
    parameters: HarperHofstadterParameters | None = None,
    *,
    bulk_nkx: int = 41,
    bulk_nky: int | None = None,
    ribbon_lx: int = 48,
    ribbon_nky: int = 181,
    edge_width: int = 4,
    edge_threshold: float = 0.5,
    side_margin: float = 1.0e-3,
) -> BulkBoundaryAnalysis:
    """Run the Stage-3 bulk-to-ribbon correspondence workflow for one parameter set."""

    params = parameters or HarperHofstadterParameters()
    topology = analyze_harper_hofstadter_topology(params, nkx=bulk_nkx, nky=bulk_nky)
    gaps = bulk_gaps_from_band_mesh(topology.band_mesh, topology.fhs.chern_numbers)
    ribbon = diagonalize_ribbon(
        lx=ribbon_lx,
        nky=ribbon_nky,
        edge_width=edge_width,
        parameters=params,
    )
    summaries = tuple(
        GapCrossingSummary(
            gap=gap,
            crossings=find_edge_crossings(
                ribbon,
                gap,
                edge_threshold=edge_threshold,
                side_margin=side_margin,
            ),
        )
        for gap in gaps
    )
    return BulkBoundaryAnalysis(
        topology=topology,
        ribbon=ribbon,
        gaps=gaps,
        crossing_summaries=summaries,
    )


__all__ = [
    "BulkBoundaryAnalysis",
    "BulkGap",
    "EdgeCrossing",
    "GapCrossingSummary",
    "analyze_bulk_boundary_correspondence",
    "bulk_gaps_from_band_mesh",
    "find_edge_crossings",
    "gap_chern_numbers",
]
