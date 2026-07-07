"""Vector schematic builders for the EJP QHE figure programme.

These functions intentionally create publication figures from primitives rather
than from manually edited drawing files.  They use no in-plot titles: panel
labels and manuscript captions carry the narrative context.
"""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure, SubFigure
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from qhe.viz.style import FIGSIZE, QHE_COLORS, set_style

PaperContext = Literal["paper", "notebook", "talk", "poster"]


def _resolve_axis(
    ax: Axes | None,
    *,
    figsize: tuple[float, float],
    context: PaperContext,
    apply_style: bool,
) -> tuple[Figure | SubFigure, Axes]:
    if apply_style:
        set_style(context=context, use_tex=False, grid=False, constrained_layout=True)
    if ax is None:
        figure, resolved_ax = plt.subplots(figsize=figsize, constrained_layout=True)
    else:
        figure, resolved_ax = ax.figure, ax
    return figure, resolved_ax


def plot_conceptual_roadmap(
    *,
    ax: Axes | None = None,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure | SubFigure, Axes]:
    """Render the manuscript's computational roadmap as a vector schematic."""
    figure, resolved_ax = _resolve_axis(
        ax,
        figsize=FIGSIZE["double_short"],
        context=context,
        apply_style=apply_style,
    )
    resolved_ax.set_axis_off()
    resolved_ax.set_xlim(0.0, 1.0)
    resolved_ax.set_ylim(0.0, 1.0)

    stages = (
        (
            0.035,
            r"Berry Curvature",
            r"Local geometry in $\mathbf{k}$ space",
            QHE_COLORS["negative"],
        ),
        (0.285, r"Chern Number", r"Gauge-invariant band integral", QHE_COLORS["highlight"]),
        (0.535, r"Ribbon Spectrum", r"Edge-localized branches", QHE_COLORS["positive"]),
        (0.785, r"Chiral Packet", r"Real-space boundary transport", QHE_COLORS["warning"]),
    )
    width = 0.18
    height = 0.42
    y = 0.34
    for x, heading, detail, colour in stages:
        box = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.022,rounding_size=0.025",
            linewidth=1.10,
            edgecolor=colour,
            facecolor="white",
            zorder=2,
        )
        resolved_ax.add_patch(box)
        resolved_ax.text(
            x + width / 2.0,
            y + 0.285,
            heading,
            ha="center",
            va="center",
            color=QHE_COLORS["ink"],
            fontweight="semibold",
        )
        resolved_ax.text(
            x + width / 2.0,
            y + 0.145,
            detail,
            ha="center",
            va="center",
            color=QHE_COLORS["muted"],
            fontsize=8.0,
            wrap=True,
        )

    for index in range(len(stages) - 1):
        start = stages[index][0] + width + 0.012
        end = stages[index + 1][0] - 0.012
        arrow = FancyArrowPatch(
            (start, y + height / 2.0),
            (end, y + height / 2.0),
            arrowstyle="-|>",
            mutation_scale=12.0,
            linewidth=1.15,
            color=QHE_COLORS["reference"],
            zorder=1,
        )
        resolved_ax.add_patch(arrow)

    resolved_ax.text(
        0.5,
        0.14,
        "A reproducible numerical sequence connects an invariant of periodic bulk bands "
        "to a measurable boundary signature.",
        ha="center",
        va="center",
        color=QHE_COLORS["ink"],
        fontsize=9.0,
    )
    return figure, resolved_ax


def plot_fhs_plaquette(
    *,
    ax: Axes | None = None,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure | SubFigure, Axes]:
    """Render the oriented FHS plaquette and overlap-link product."""
    figure, resolved_ax = _resolve_axis(
        ax,
        figsize=FIGSIZE["single_square"],
        context=context,
        apply_style=apply_style,
    )
    resolved_ax.set_axis_off()
    resolved_ax.set_xlim(-0.22, 1.44)
    resolved_ax.set_ylim(-0.30, 1.26)

    corners = {
        "k": (0.0, 0.0),
        "kx": (1.0, 0.0),
        "ky": (0.0, 1.0),
        "kxy": (1.0, 1.0),
    }
    for label, (x, y) in corners.items():
        resolved_ax.scatter([x], [y], s=30.0, color=QHE_COLORS["ink"], zorder=4)
        display = {
            "k": r"$\mathbf{k}$",
            "kx": r"$\mathbf{k}+\hat{1}$",
            "ky": r"$\mathbf{k}+\hat{2}$",
            "kxy": r"$\mathbf{k}+\hat{1}+\hat{2}$",
        }[label]
        offset = (-0.02, -0.12) if label == "k" else (0.02, -0.12)
        if label == "ky":
            offset = (-0.18, 0.02)
        if label == "kxy":
            offset = (0.02, 0.02)
        resolved_ax.text(x + offset[0], y + offset[1], display, color=QHE_COLORS["ink"])

    arrow_specs = (
        ((0.06, 0.0), (0.92, 0.0), r"$U_1(\mathbf{k})$", (0.50, -0.15)),
        ((1.0, 0.06), (1.0, 0.92), r"$U_2(\mathbf{k}+\hat{1})$", (1.13, 0.50)),
        ((0.94, 1.0), (0.08, 1.0), r"$U_1^{-1}(\mathbf{k}+\hat{2})$", (0.50, 1.14)),
        ((0.0, 0.94), (0.0, 0.08), r"$U_2^{-1}(\mathbf{k})$", (-0.20, 0.50)),
    )
    for start, end, label, position in arrow_specs:
        resolved_ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=12.0,
                linewidth=1.25,
                color=QHE_COLORS["highlight"],
                zorder=3,
            )
        )
        resolved_ax.text(
            position[0],
            position[1],
            label,
            ha="center",
            va="center",
            fontsize=8.2,
            color=QHE_COLORS["ink"],
        )

    resolved_ax.text(
        0.50,
        -0.25,
        r"$\widetilde F_{12}(\mathbf{k})=-\arg\!\left[U_1U_2U_1^{-1}U_2^{-1}\right]$",
        ha="center",
        va="center",
        color=QHE_COLORS["ink"],
        fontsize=9.2,
    )
    return figure, resolved_ax


__all__ = ["plot_conceptual_roadmap", "plot_fhs_plaquette"]
