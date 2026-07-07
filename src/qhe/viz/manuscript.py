"""High-level manuscript figure builders for the completed static QHE workflow."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from qhe.boundary import BulkBoundaryAnalysis, EdgeCrossing
from qhe.viz.edge import plot_bulk_boundary_spectrum, plot_crossing_profiles
from qhe.viz.style import FIGSIZE, panel_label, set_style

PaperContext = Literal["paper", "notebook", "talk", "poster"]


def _representative_crossings(analysis: BulkBoundaryAnalysis) -> tuple[EdgeCrossing, ...]:
    """Select one crossing on each boundary from each resolved bulk gap."""
    selected: list[EdgeCrossing] = []
    for summary in analysis.crossing_summaries:
        if summary.left_crossings:
            selected.append(summary.left_crossings[0])
        if summary.right_crossings:
            selected.append(summary.right_crossings[0])
    return tuple(selected)


def plot_ribbon_bulk_boundary_figure(
    analysis: BulkBoundaryAnalysis,
    *,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure, np.ndarray]:
    """Create a two-panel measurable bulk-boundary correspondence figure."""
    if apply_style:
        set_style(context=context, use_tex=False, grid=False, constrained_layout=True)
    figure, axes = plt.subplots(
        1,
        2,
        figsize=FIGSIZE["wide"],
        constrained_layout=True,
        width_ratios=(1.28, 1.0),
    )
    plot_bulk_boundary_spectrum(
        analysis,
        ax=axes[0],
        marker_size=7.0,
        show_colorbar=True,
        context=context,
        apply_style=False,
    )
    panel_label(axes[0], "(a)")

    crossings = _representative_crossings(analysis)
    plot_crossing_profiles(
        analysis.ribbon,
        crossings,
        ax=axes[1],
        context=context,
        apply_style=False,
    )
    panel_label(axes[1], "(b)")
    return figure, np.asarray(axes, dtype=object)


__all__ = ["plot_ribbon_bulk_boundary_figure"]
