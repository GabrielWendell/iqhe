"""Figure builders for bulk topology, curvature validation, and teaching panels."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import Normalize, TwoSlopeNorm
from matplotlib.figure import Figure

from qhe.models import (
    DiracParameters,
    HarperHofstadterParameters,
    magnetic_brillouin_zone,
    massive_dirac_berry_curvature,
    massive_dirac_energies,
)
from qhe.topology import ConvergenceResult, TopologyAnalysis
from qhe.viz.style import (
    FIGSIZE,
    QHE_COLORS,
    QHE_LINE_PALETTE,
    annotate_textbox,
    panel_label,
    set_style,
    style_axes,
    style_colorbar,
    style_legend,
)

PaperContext = Literal["paper", "notebook", "talk", "poster"]
LegendLocation = Literal[
    "best",
    "upper right",
    "upper left",
    "lower left",
    "lower right",
    "right",
    "center left",
    "center right",
    "lower center",
    "upper center",
    "center",
]
LegendAnchor = tuple[float, float] | tuple[float, float, float, float]


def _prepare_figure(
    *,
    figsize: tuple[float, float],
    context: PaperContext,
    apply_style: bool,
    nrows: int = 1,
    ncols: int = 1,
) -> tuple[Figure, np.ndarray]:
    if apply_style:
        set_style(context=context, use_tex=False, grid=False, constrained_layout=True)
    figure, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=figsize,
        constrained_layout=True,
        squeeze=False,
    )
    return figure, axes


def plot_massive_dirac_warmup(
    parameters: DiracParameters | None = None,
    *,
    kmax: float = 1.2,
    n_line: int = 301,
    n_map: int = 151,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure, np.ndarray]:
    """Plot a compact massive-Dirac spectrum/curvature warm-up without axis titles."""
    if kmax <= 0.0 or n_line < 3 or n_map < 3:
        raise ValueError("kmax must be positive and sample counts must be at least three.")
    params = parameters or DiracParameters()
    figure, axes = _prepare_figure(
        figsize=FIGSIZE["double_short"],
        context=context,
        apply_style=apply_style,
        nrows=1,
        ncols=3,
    )
    ax_spectrum, ax_line, ax_map = axes[0]

    k_line = np.linspace(-kmax, kmax, n_line)
    energies = np.asarray([massive_dirac_energies(kx, 0.0, params) for kx in k_line])
    ax_spectrum.plot(k_line, energies[:, 0], color=QHE_COLORS["negative"], label=r"$E_-$")
    ax_spectrum.plot(k_line, energies[:, 1], color=QHE_COLORS["positive"], label=r"$E_+$")
    style_axes(
        ax_spectrum,
        xlabel=r"$k_x$ at $k_y=0$",
        ylabel=r"Energy $E$",
        grid=True,
        grid_axis="y",
    )
    style_legend(ax_spectrum, loc="upper center", ncols=2)
    panel_label(ax_spectrum, "(a)")

    curvature_line = np.asarray(
        [massive_dirac_berry_curvature(kx, 0.0, params)[0] for kx in k_line]
    )
    ax_line.plot(k_line, curvature_line, color=QHE_COLORS["highlight"])
    style_axes(
        ax_line,
        xlabel=r"$k_x$ at $k_y=0$",
        ylabel=r"$\Omega_-(k_x,0)$",
        grid=True,
        grid_axis="y",
    )
    panel_label(ax_line, "(b)")

    coordinates = np.linspace(-kmax, kmax, n_map)
    kx_grid, ky_grid = np.meshgrid(coordinates, coordinates, indexing="xy")
    curvature_map = np.empty_like(kx_grid)
    for index in np.ndindex(kx_grid.shape):
        curvature_map[index] = massive_dirac_berry_curvature(
            float(kx_grid[index]), float(ky_grid[index]), params
        )[0]
    image = ax_map.pcolormesh(
        kx_grid,
        ky_grid,
        curvature_map,
        shading="auto",
        cmap="cividis",
    )
    colorbar = figure.colorbar(image, ax=ax_map, pad=0.018, fraction=0.055)
    style_colorbar(colorbar, label=r"$\Omega_-$", minor=False)
    style_axes(
        ax_map,
        xlabel=r"$k_x$",
        ylabel=r"$k_y$",
        grid=False,
        minor=False,
    )
    ax_map.set_aspect("equal", adjustable="box")
    panel_label(ax_map, "(c)")
    return figure, axes


def _magnetic_path(
    parameters: HarperHofstadterParameters,
    points_per_segment: int,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    tuple[float, ...],
    tuple[str, ...],
]:
    if points_per_segment < 2:
        raise ValueError("points_per_segment must be at least two.")
    zone = magnetic_brillouin_zone(parameters)
    gamma = (0.0, 0.0)
    x_point = (zone.kx_max, 0.0)
    m_point = (zone.kx_max, zone.ky_max)
    y_point = (0.0, zone.ky_max)
    vertices = (gamma, x_point, m_point, y_point, gamma)
    labels = (r"$\Gamma$", r"$X$", r"$M$", r"$Y$", r"$\Gamma$")
    kx: list[float] = []
    ky: list[float] = []
    coordinate: list[float] = []
    tick_positions = [0.0]
    current = 0.0
    for segment_index, (first, second) in enumerate(zip(vertices[:-1], vertices[1:], strict=True)):
        local = np.linspace(
            0.0,
            1.0,
            points_per_segment,
            endpoint=segment_index == len(vertices) - 2,
        )
        if segment_index > 0:
            local = local[1:]
        dx = second[0] - first[0]
        dy = second[1] - first[1]
        segment_length = float(np.hypot(dx, dy))
        for fraction in local:
            kx.append(first[0] + fraction * dx)
            ky.append(first[1] + fraction * dy)
            coordinate.append(current + fraction * segment_length)
        current += segment_length
        tick_positions.append(current)
    return (
        np.asarray(kx, dtype=float),
        np.asarray(ky, dtype=float),
        np.asarray(coordinate, dtype=float),
        tuple(tick_positions),
        labels,
    )


def plot_hofstadter_bulk_bands(
    analysis: TopologyAnalysis,
    parameters: HarperHofstadterParameters | None = None,
    *,
    points_per_segment: int = 121,
    legend_loc: LegendLocation = "best",
    legend_bbox_to_anchor: LegendAnchor | None = None,
    legend_ncols: int = 1,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure, Axes]:
    """Plot magnetic-subband dispersions along a labelled magnetic-zone path.

    Parameters
    ----------
    legend_loc:
        Matplotlib legend location.  With the default ``"best"``, Matplotlib
        selects an in-axes location that minimizes overlap with the plotted
        bands.  To position a legend manually, use a fixed location together
        with ``legend_bbox_to_anchor``.
    legend_bbox_to_anchor:
        Optional axes-relative anchor coordinates.  For example,
        ``legend_loc="upper right", legend_bbox_to_anchor=(0.98, 0.98)``
        pins the upper-right corner of the legend near the upper-right corner
        of the plotting area.  Coordinates in ``[0, 1]`` lie inside the axes;
        values outside that interval place the legend outside the axes.
    legend_ncols:
        Number of legend columns. The default is ``1`` so the band entries
        are stacked vertically. Set it to a larger value only when a compact
        multi-column legend is explicitly desired.
    """
    if legend_ncols < 1:
        raise ValueError("legend_ncols must be at least one.")

    params = parameters or HarperHofstadterParameters()
    figure, axes = _prepare_figure(
        figsize=FIGSIZE["double_short"],
        context=context,
        apply_style=apply_style,
    )
    ax = axes[0, 0]
    kx, ky, path_coordinate, ticks, labels = _magnetic_path(params, points_per_segment)
    from qhe.models import bloch_hamiltonian

    energies = np.empty((kx.size, params.q), dtype=float)
    for index, (kx_value, ky_value) in enumerate(zip(kx, ky, strict=True)):
        hamiltonian = bloch_hamiltonian(
            float(kx_value),
            float(ky_value),
            params,
        )
        energies[index] = np.linalg.eigvalsh(hamiltonian)

    chern = np.rint(analysis.fhs.chern_numbers).astype(int)
    for band in range(params.q):
        signed = f"{chern[band]:+d}"
        ax.plot(
            path_coordinate,
            energies[:, band],
            color=QHE_LINE_PALETTE[band % len(QHE_LINE_PALETTE)],
            label=rf"Band {band + 1}: $C={signed}$",
        )
    for position in ticks[1:-1]:
        ax.axvline(position, color=QHE_COLORS["grid"], linewidth=0.75, zorder=0)
    ax.set_xticks(ticks, labels)
    style_axes(
        ax,
        xlabel="Magnetic Brillouin-zone Path",
        ylabel=r"Energy $E$",
        grid=True,
        grid_axis="y",
    )
    legend = style_legend(ax, loc=legend_loc, ncols=legend_ncols)
    if legend is not None and legend_bbox_to_anchor is not None:
        # Use axes coordinates so users can tune the horizontal and vertical
        # placement without depending on data limits or figure dimensions.
        legend.set_bbox_to_anchor(legend_bbox_to_anchor, transform=ax.transAxes)
    panel_label(ax, "(a)")
    return figure, ax


def _map_axes(
    axis: Axes,
    field: np.ndarray,
    analysis: TopologyAnalysis,
    *,
    cmap: str,
    norm: Normalize | None,
):
    mesh = analysis.band_mesh.mesh
    return axis.pcolormesh(
        mesh.kx,
        mesh.ky,
        field.T,
        shading="auto",
        cmap=cmap,
        norm=norm,
    )


def plot_fhs_kubo_validation(
    analysis: TopologyAnalysis,
    convergence: ConvergenceResult,
    *,
    band_index: int = 0,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure, np.ndarray]:
    """Build a six-panel compatible FHS/Kubo validation figure for one isolated band."""
    if not 0 <= band_index < analysis.band_mesh.band_count:
        raise IndexError("band_index is outside the sampled band range.")
    figure, axes = _prepare_figure(
        figsize=FIGSIZE["wide"],
        context=context,
        apply_style=apply_style,
        nrows=2,
        ncols=3,
    )
    fhs = analysis.fhs.curvature_density[..., band_index]
    kubo = analysis.comparison.kubo_plaquette_average[..., band_index]
    residual = analysis.comparison.residual[..., band_index]
    vmax = float(max(np.max(np.abs(fhs)), np.max(np.abs(kubo))))
    density_norm = Normalize(vmin=-vmax, vmax=vmax)
    residual_limit = float(np.max(np.abs(residual)))
    residual_norm = TwoSlopeNorm(vmin=-residual_limit, vcenter=0.0, vmax=residual_limit)

    labels = ("(a)", "(b)", "(c)")
    plots = (
        (axes[0, 0], fhs, "cividis", density_norm, r"$\Omega_{\mathrm{FHS}}$"),
        (axes[0, 1], kubo, "cividis", density_norm, r"$\overline{\Omega}_{\mathrm{Kubo}}$"),
        (axes[0, 2], residual, "coolwarm", residual_norm, r"$\Delta\Omega$"),
    )
    for label, (axis, field, cmap, norm, colorbar_label) in zip(labels, plots, strict=True):
        image = _map_axes(axis, field, analysis, cmap=cmap, norm=norm)
        colorbar = figure.colorbar(image, ax=axis, pad=0.015, fraction=0.050)
        style_colorbar(colorbar, label=colorbar_label, minor=False)
        style_axes(axis, xlabel=r"$k_x$", ylabel=r"$k_y$", grid=False, minor=False)
        axis.set_aspect("auto")
        panel_label(axis, label)

    band_count = convergence.fhs_chern_numbers.shape[1]
    line_styles = ("-", "--", ":")
    markers = ("o", "s", "^")
    for band in range(band_count):
        color = QHE_LINE_PALETTE[band % len(QHE_LINE_PALETTE)]
        expected = round(float(convergence.fhs_chern_numbers[-1, band]))
        axes[1, 0].plot(
            convergence.mesh_sizes,
            convergence.fhs_chern_numbers[:, band],
            color=color,
            marker=markers[band % len(markers)],
            linestyle=line_styles[band % len(line_styles)],
            label=rf"Band {band + 1}",
        )
        axes[1, 0].plot(
            convergence.mesh_sizes,
            convergence.kubo_chern_numbers[:, band],
            color=color,
            marker="x",
            linestyle="none",
            label="_nolegend_",
        )
        axes[1, 0].axhline(expected, color=color, linewidth=0.60, alpha=0.32, zorder=0)
    style_axes(
        axes[1, 0],
        xlabel=r"Mesh Size $N_k$",
        ylabel=r"Chern Estimate",
        grid=True,
        grid_axis="y",
    )
    style_legend(axes[1, 0], loc="best", ncols=1)
    annotate_textbox(
        axes[1, 0],
        "Lines: FHS\n$\\times$ : Kubo",
        x=0.93,
        y=0.77,
        va="center",
        fontsize=8.0,
    )
    panel_label(axes[1, 0], "(d)")

    for band in range(band_count):
        axes[1, 1].plot(
            convergence.mesh_sizes,
            convergence.l2_errors[:, band],
            color=QHE_LINE_PALETTE[band % len(QHE_LINE_PALETTE)],
            marker=markers[band % len(markers)],
            label=rf"Band {band + 1}",
        )
    style_axes(
        axes[1, 1],
        xlabel=r"Mesh Size $N_k$",
        ylabel=r"$L^2$ Residual",
        yscale="log",
        grid=True,
        grid_axis="y",
    )
    style_legend(axes[1, 1], loc="best", ncols=1)
    panel_label(axes[1, 1], "(e)")

    for band in range(band_count):
        axes[1, 2].plot(
            convergence.mesh_sizes,
            convergence.linf_errors[:, band],
            color=QHE_LINE_PALETTE[band % len(QHE_LINE_PALETTE)],
            marker=markers[band % len(markers)],
            label=rf"Band {band + 1}",
        )
    style_axes(
        axes[1, 2],
        xlabel=r"Mesh Size $N_k$",
        ylabel=r"$L^\infty$ Residual",
        yscale="log",
        grid=True,
        grid_axis="y",
    )
    style_legend(axes[1, 2], loc="best", ncols=1)
    panel_label(axes[1, 2], "(f)")
    return figure, axes


__all__ = [
    "plot_fhs_kubo_validation",
    "plot_hofstadter_bulk_bands",
    "plot_massive_dirac_warmup",
]
