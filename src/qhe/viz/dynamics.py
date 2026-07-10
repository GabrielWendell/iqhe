"""Stage-6 manuscript figures for chiral edge-wave-packet dynamics."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.image import AxesImage

from qhe.dynamics import DynamicsAnalysis
from qhe.dynamics.currents import bond_currents
from qhe.viz.style import FIGSIZE, QHE_COLORS, panel_label, set_style, style_axes, style_colorbar

PaperContext = Literal["paper", "notebook", "talk", "poster"]


def _time_indices(n_times: int) -> tuple[int, int, int]:
    return (0, max(1, n_times // 2), n_times - 1)


def _density_grid(state: np.ndarray, lx: int, ly: int) -> np.ndarray:
    return np.abs(np.asarray(state).reshape(lx, ly)) ** 2


def _plot_density(
    ax: Axes,
    density: np.ndarray,
    *,
    vmax: float,
    time: float,
    defect_position: int | None = None,
) -> AxesImage:
    image = ax.imshow(
        density.T,
        origin="lower",
        aspect="auto",
        vmin=0.0,
        vmax=vmax,
        cmap="magma",
        interpolation="nearest",
        rasterized=True,
    )
    if defect_position is not None:
        ax.plot(
            [0.0, 0.0],
            [defect_position, defect_position + 1],
            color="white",
            linewidth=2.0,
            solid_capstyle="round",
            zorder=5,
        )
        ax.plot(
            [0.0, 0.0],
            [defect_position, defect_position + 1],
            color=QHE_COLORS["warning"],
            linewidth=1.0,
            solid_capstyle="round",
            zorder=6,
        )
    ax.text(
        0.05,
        0.90,
        rf"$t={time:.1f}$",
        transform=ax.transAxes,
        color="white",
        fontsize=8.5,
        bbox={"boxstyle": "round,pad=0.18", "fc": "black", "ec": "none", "alpha": 0.58},
    )
    style_axes(ax, xlabel=r"$m$", ylabel=r"$n$", grid=False)
    return image


def plot_chiral_dynamics_figure(
    analysis: DynamicsAnalysis,
    *,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure, np.ndarray]:
    """Create Figure 7: edge-projected packet dynamics and diagnostics."""

    if apply_style:
        set_style(context=context, use_tex=False, grid=False, constrained_layout=True)
    fig, axes = plt.subplots(
        2,
        3,
        figsize=(7.5, 5.8),
        constrained_layout=True,
        height_ratios=(1.0, 0.86),
    )
    top_axes = axes[0]
    bottom_axes = axes[1]
    indices = _time_indices(analysis.config.n_times)
    densities = [
        _density_grid(analysis.clean.states[index], analysis.config.lx, analysis.config.ly)
        for index in indices
    ]
    vmax = float(max(np.max(density) for density in densities))
    image: AxesImage | None = None
    for ax, index, label in zip(top_axes, indices, ("(a)", "(b)", "(c)"), strict=True):
        image = _plot_density(
            ax,
            _density_grid(analysis.clean.states[index], analysis.config.lx, analysis.config.ly),
            vmax=vmax,
            time=float(analysis.config.times[index]),
        )
        panel_label(ax, label, x=0.01, y=0.98)
    if image is not None:
        cbar = fig.colorbar(image, ax=list(top_axes), pad=0.012, fraction=0.025)
        style_colorbar(cbar, label=r"Probability $|\psi(m,n,t)|^2$")

    ax = bottom_axes[0]
    ax.plot(analysis.config.times, analysis.clean.edge_probability, label=r"$P_{\mathrm{edge}}(t)$")
    ax.plot(analysis.config.times, analysis.clean.bulk_probability, linestyle="--", label=r"$P_{\mathrm{bulk}}(t)$")
    style_axes(ax, xlabel=r"Time $t$", ylabel="Probability", grid=True, grid_axis="y")
    ax.set_ylim(-0.03, 1.03)
    ax.legend(loc="best", frameon=True)
    panel_label(ax, "(d)")

    ax = bottom_axes[1]
    ax.plot(analysis.config.times, analysis.clean.coordinate, label=r"Packet Coordinate")
    fit = analysis.clean.velocity_fit
    fit_line = fit.velocity * analysis.config.times + fit.intercept
    ax.plot(analysis.config.times, fit_line, linestyle="--", label=rf"Fit: $v={fit.velocity:.2f}$")
    style_axes(ax, xlabel=r"Time $t$", ylabel=r"Edge Coordinate $s(t)$", grid=True, grid_axis="y")
    ax.legend(loc="best", frameon=True)
    panel_label(ax, "(e)")

    ax = bottom_axes[2]
    currents = bond_currents(
        analysis.clean.states[indices[1]],
        analysis.config.lx,
        analysis.config.ly,
        analysis.config.parameters,
        hbar=analysis.config.hbar,
    )
    y = np.arange(analysis.config.ly - 1)
    edge_slice = currents.jy[: analysis.config.edge_width, :]
    ax.plot(y + 0.5, np.mean(edge_slice, axis=0), color=QHE_COLORS["left_edge"])
    ax.axhline(0.0, color=QHE_COLORS["reference"], linewidth=0.8, linestyle=":")
    style_axes(
        ax,
        xlabel=r"Longitudinal Bond Coordinate $n+1/2$",
        ylabel=r"Mean Edge Current $J_y$",
        grid=True,
        grid_axis="y",
    )
    panel_label(ax, "(f)")
    return fig, axes.ravel()

def plot_velocity_defect_figure(
    analysis: DynamicsAnalysis,
    *,
    context: PaperContext = "paper",
    apply_style: bool = True,
) -> tuple[Figure, np.ndarray]:
    """Create Figure 8: velocity validation and weak-link-defect routing."""

    if apply_style:
        set_style(context=context, use_tex=False, grid=False, constrained_layout=True)
    fig = plt.figure(figsize=FIGSIZE["wide"], constrained_layout=True)
    axes = fig.subplots(2, 2)
    flat = axes.ravel()

    ax = flat[0]
    labels = ["Ribbon Group", "Clean Packet", "Defect Packet"]
    velocities = [
        analysis.group_velocity,
        analysis.clean.velocity_fit.velocity,
        analysis.defect.velocity_fit.velocity,
    ]
    x = np.arange(len(labels))
    ax.axhline(analysis.group_velocity, color=QHE_COLORS["reference"], linestyle="--", linewidth=0.9)
    ax.scatter(x, velocities, s=44.0, edgecolors="black", zorder=3)
    ax.set_xticks(x, labels, rotation=20, ha="right")
    style_axes(ax, xlabel="", ylabel=r"Velocity", grid=True, grid_axis="y")
    panel_label(ax, "(a)")

    ax = flat[1]
    ax.plot(analysis.config.times, analysis.clean.edge_probability, label="Clean")
    ax.plot(analysis.config.times, analysis.defect.edge_probability, linestyle="--", label="Defect")
    style_axes(ax, xlabel=r"Time $t$", ylabel=r"$P_{\mathrm{edge}}(t)$", grid=True, grid_axis="y")
    ax.set_ylim(0.0, 1.03)
    ax.legend(loc="best", frameon=True)
    panel_label(ax, "(b)")

    index = _time_indices(analysis.config.n_times)[1]
    densities = [
        _density_grid(analysis.clean.states[index], analysis.config.lx, analysis.config.ly),
        _density_grid(analysis.defect.states[index], analysis.config.lx, analysis.config.ly),
    ]
    vmax = float(max(np.max(density) for density in densities))
    image = _plot_density(
        flat[2],
        densities[0],
        vmax=vmax,
        time=float(analysis.config.times[index]),
    )
    panel_label(flat[2], "(c)")
    _plot_density(
        flat[3],
        densities[1],
        vmax=vmax,
        time=float(analysis.config.times[index]),
        defect_position=analysis.weak_link.position,
    )
    panel_label(flat[3], "(d)")
    cbar = fig.colorbar(image, ax=[flat[2], flat[3]], pad=0.012, fraction=0.042)
    style_colorbar(cbar, label=r"Probability $|\psi|^2$")
    return fig, flat


__all__ = ["plot_chiral_dynamics_figure", "plot_velocity_defect_figure"]
