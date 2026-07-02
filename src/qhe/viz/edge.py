"""Publication-quality figure builders for measurable QHE edge physics.

The functions in this module implement the Stage-3 visual conventions:
edge participation is represented by a perceptually uniform colour scale,
crossing orientation uses redundant colour-and-marker encoding, and all
axes follow the manuscript style defined in :mod:`qhe.style`.

Recommended usage
-----------------
Place ``style.py`` beside this module (or expose it as ``qhe.style``) and
call the plotting functions normally.  By default, each function applies
the paper context.  To control the global appearance once for a full
figure-building script, call ``qhe.style.set_style(context="paper")``
before creating any figures and pass ``apply_style=False`` below.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure, SubFigure
import numpy as np
from matplotlib.colors import Normalize

from qhe.boundary import BulkBoundaryAnalysis, EdgeCrossing, RibbonSpectrum
from .style import (
        FIGSIZE,
        QHE_COLORS,
        crossing_color,
        edge_side_color,
        set_style,
        style_axes,
        style_colorbar,
        style_legend,
    )



PaperContext = Literal["paper", "notebook", "talk", "poster"]


def _prepare_axes(
    ax: Axes | None,
    *,
    figsize: tuple[float, float],
    context: PaperContext,
    apply_style: bool,
) -> tuple[Figure | SubFigure, Axes]:
    """Resolve a target axis and, when requested, activate the paper style."""
    if apply_style:
        set_style(context=context, grid=False, constrained_layout=True)

    if ax is None:
        figure, resolved_ax = plt.subplots(
            figsize=figsize,
            constrained_layout=True,
        )
    else:
        figure, resolved_ax = ax.figure, ax
    return figure, resolved_ax


def _edge_participation_norm(values: np.ndarray) -> Normalize:
    """Construct a robust normalisation for a probability-like edge score."""
    finite_values = np.asarray(values, dtype=float)
    finite_values = finite_values[np.isfinite(finite_values)]

    if finite_values.size == 0:
        return Normalize(vmin=0.0, vmax=1.0)

    # Edge participation is mathematically expected to lie in [0, 1].  The
    # fallback covers small numerical excursions without silently clipping
    # informative values.
    lower = min(0.0, float(np.min(finite_values)))
    upper = max(1.0, float(np.max(finite_values)))
    if np.isclose(lower, upper):
        upper = lower + 1.0
    return Normalize(vmin=lower, vmax=upper, clip=True)


def plot_ribbon_spectrum(
    ribbon: RibbonSpectrum,
    *,
    ax: Axes | None = None,
    marker_size: float = 8.0,
    cmap: str = "cividis",
    show_colorbar: bool = True,
    colorbar_label: str = r"Edge Participation $P_{\mathrm{edge}}$",
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure | SubFigure, Axes]:
    """Plot a ribbon spectrum with edge participation encoded by colour.

    The density-like edge participation is displayed with the perceptually
    uniform ``cividis`` colour map.  Markers are rasterized inside vector
    exports to keep PDFs compact while preserving vector text and axes.

    Parameters
    ----------
    ribbon:
        Ribbon spectrum and edge-localization data.
    marker_size:
        Area of a spectral marker in points squared.
    cmap:
        Matplotlib sequential colour map used for edge participation.
    show_colorbar:
        Whether to add the scalar-key colour bar.
    """
    if marker_size <= 0.0:
        raise ValueError("marker_size must be strictly positive.")

    figure, ax = _prepare_axes(
        ax,
        figsize=FIGSIZE["double_short"],
        context=context,
        apply_style=apply_style,
    )

    ky_grid, _ = np.meshgrid(ribbon.ky, np.arange(ribbon.lx), indexing="ij")
    norm = _edge_participation_norm(ribbon.edge_participation)
    collection = ax.scatter(
        ky_grid.ravel(),
        ribbon.energies.ravel(),
        c=ribbon.edge_participation.ravel(),
        cmap=cmap,
        norm=norm,
        s=marker_size,
        linewidths=0.0,
        alpha=0.96,
        rasterized=True,
        zorder=2,
    )

    if show_colorbar:
        colorbar = figure.colorbar(collection, ax=ax, pad=0.018, fraction=0.055)
        style_colorbar(colorbar, label=colorbar_label, minor=False)

    style_axes(
        ax,
        xlabel=r"Transverse Wave Vector $k_y$",
        ylabel=r"Energy $E$",
        grid=True,
        grid_axis="y",
    )
    ax.margins(x=0.015, y=0.045)
    return figure, ax


def plot_crossing_profiles(
    ribbon: RibbonSpectrum,
    crossings: Sequence[EdgeCrossing],
    *,
    ax: Axes | None = None,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure | SubFigure, Axes]:
    """Plot transverse probability profiles at selected edge-state crossings.

    Left and right edge localization are encoded with a semantic
    colour-and-line-style pair, making the result interpretable in
    grayscale and for readers with colour-vision deficiencies.
    """
    if not crossings:
        raise ValueError("At least one crossing is required to plot edge profiles.")

    figure, ax = _prepare_axes(
        ax,
        figsize=FIGSIZE["double_short"],
        context=context,
        apply_style=apply_style,
    )

    x = np.arange(ribbon.lx)
    side_counts: dict[str, int] = {}
    for crossing in crossings:
        state = ribbon.eigenvectors[crossing.segment_index, :, crossing.band_index]
        probability = np.abs(state) ** 2

        side_key = str(crossing.side).strip().lower()
        occurrence = side_counts.get(side_key, 0)
        side_counts[side_key] = occurrence + 1

        colour = edge_side_color(side_key)
        linestyle = "-" if side_key.startswith("left") else "--"
        linewidth = 1.65 if occurrence == 0 else 1.20
        alpha = 0.98 if occurrence == 0 else 0.72
        display_side = {"left": "Left", "right": "Right"}.get(
            side_key,
            str(crossing.side).strip().capitalize(),
        )
        label = (
            rf"{display_side} Edge: $k_y={crossing.ky:.3f}$, "
            rf"$\partial E/\partial k_y={crossing.slope:.3f}$"
        )
        ax.plot(
            x,
            probability,
            color=colour,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            label=label,
            zorder=3,
        )
    style_axes(
        ax,
        xlabel=r"Transverse Lattice Site $m$",
        ylabel=r"Probability Density $|\psi_m|^2$",
        grid=True,
        grid_axis="y",
    )
    ax.set_ylim(bottom=0.0)
    ax.margins(x=0.015, y=0.10)
    style_legend(ax, ncols=1, above=True)
    return figure, ax


def plot_bulk_boundary_spectrum(
    analysis: BulkBoundaryAnalysis,
    *,
    ax: Axes | None = None,
    marker_size: float = 8.0,
    cmap: str = "cividis",
    show_colorbar: bool = True,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure | SubFigure, Axes]:
    """Plot a ribbon spectrum, bulk-gap reference energies, and crossings.

    Dashed grey lines identify bulk-gap reference energies.  Upward and
    downward triangles represent opposite crossing orientations; they also
    use the warm/cool semantic colours to provide redundant encoding.
    """
    figure, ax = plot_ribbon_spectrum(
        analysis.ribbon,
        ax=ax,
        marker_size=marker_size,
        cmap=cmap,
        show_colorbar=show_colorbar,
        context=context,
        apply_style=apply_style,
    )

    used_labels: set[str] = set()
    for summary in analysis.crossing_summaries:
        line_label = "Bulk-gap Reference"
        if line_label in used_labels:
            line_label = "_nolegend_"
        else:
            used_labels.add("Bulk-gap Reference")

        ax.axhline(
            summary.gap.reference_energy,
            color=QHE_COLORS["reference"],
            linestyle="--",
            linewidth=0.90,
            alpha=0.86,
            label=line_label,
            zorder=1,
        )

        for crossing in summary.crossings:
            is_positive = crossing.orientation > 0
            marker = "^" if is_positive else "v"
            label = "Positive Crossing" if is_positive else "Negative Crossing"
            if label in used_labels:
                label = "_nolegend_"
            else:
                used_labels.add(label)

            ax.scatter(
                [crossing.ky],
                [crossing.energy],
                marker=marker,
                s=44.0,
                edgecolors=crossing_color(crossing.orientation),
                facecolors="white",
                linewidths=1.00,
                label=label,
                zorder=5,
            )

    style_legend(ax, ncols=3, above=True)
    return figure, ax


__all__ = [
    "plot_bulk_boundary_spectrum",
    "plot_crossing_profiles",
    "plot_ribbon_spectrum",
]
