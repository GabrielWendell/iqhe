"""Publication-quality Matplotlib style utilities for the QHE project.

This module centralizes the visual language used in the computational
Quantum Hall Effect manuscript.  The defaults are designed for compact
journal figures: serif text, inward ticks on all sides, restrained grids,
colorblind-aware categorical colors, perceptually uniform scalar maps, and
vector-friendly export settings.

Typical usage
-------------
>>> from qhe.style import set_style, style_axes, save_figure
>>> set_style(context="paper", use_tex="auto")
>>> fig, ax = plt.subplots(figsize=FIGSIZE["single"])
>>> ax.plot(x, y)
>>> style_axes(ax, xlabel=r"$k_y$", ylabel=r"energy $E$")
>>> save_figure(fig, "reports/figures/example.pdf", formats=("png",))
"""

from __future__ import annotations

import shutil
from collections.abc import Iterable, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Literal, TypeAlias, cast

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure
from matplotlib.legend import Legend

__all__ = [
    "GridAxis",
    "LegendLocation",
    "FIGSIZE",
    "QHE_COLORS",
    "QHE_LINE_PALETTE",
    "build_rcparams",
    "set_style",
    "paper_style",
    "style_axes",
    "style_colorbar",
    "style_legend",
    "panel_label",
    "annotate_textbox",
    "save_figure",
    "edge_side_color",
    "crossing_color",
    "add_zero_line",
]

GridAxis = Literal["x", "y", "both"]

# Matplotlib accepts either one of its canonical location strings, an integer
# location code, or a two-coordinate anchor.  Keeping the literal values here
# prevents Pylance from widening ``loc`` to ``str`` before calling ``Axes.legend``.
LegendLocation: TypeAlias = (
    Literal[
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
    | int
    | tuple[float, float]
)

# -------------------------------------------------------------------------
# Semantic colours
# -------------------------------------------------------------------------

# The palette is based on high-contrast, colour-vision-deficiency-aware hues.
# It is intentionally compact: colours are assigned physical meanings rather
# than being used decoratively.
QHE_COLORS: dict[str, str] = {
    "ink": "#1F2937",
    "muted": "#6B7280",
    "grid": "#D1D5DB",
    "reference": "#4B5563",
    "positive": "#D55E00",
    "negative": "#0072B2",
    "left_edge": "#0072B2",
    "right_edge": "#D55E00",
    "bulk": "#6B7280",
    "highlight": "#009E73",
    "warning": "#CC79A7",
    "gap": "#7A7A7A",
}

# Default categorical line colours for curves where no more specific
# physical meaning is available.
QHE_LINE_PALETTE: tuple[str, ...] = (
    "#0072B2",
    "#D55E00",
    "#009E73",
    "#CC79A7",
    "#E69F00",
    "#56B4E9",
    "#6B7280",
)

# Compact single- and double-column article dimensions in inches.
FIGSIZE: dict[str, tuple[float, float]] = {
    "single": (3.45, 2.45),
    "single_square": (3.45, 3.15),
    "single_tall": (3.45, 3.70),
    "double": (7.10, 4.45),
    "double_short": (7.10, 3.25),
    "wide": (7.50, 4.70),
}


def _latex_available() -> bool:
    """Return whether a LaTeX executable is available on this system."""
    return shutil.which("latex") is not None


def _resolve_usetex(use_tex: bool | str) -> bool:
    """Resolve the explicit or automatic TeX preference."""
    if isinstance(use_tex, str):
        if use_tex != "auto":
            raise ValueError("use_tex must be True, False, or 'auto'.")
        return _latex_available()
    return bool(use_tex)


def _validate_context(context: str) -> tuple[float, float, float]:
    presets: dict[str, tuple[float, float, float]] = {
        "paper": (10.4, 1.30, 4.8),
        "notebook": (12.0, 1.50, 5.4),
        "talk": (14.5, 1.90, 6.2),
        "poster": (18.0, 2.20, 7.2),
    }
    try:
        return presets[context]
    except KeyError as exc:
        valid = ", ".join(presets)
        raise ValueError(f"Unsupported context {context!r}. Choose one of: {valid}.") from exc


def build_rcparams(
    *,
    context: str = "paper",
    use_tex: bool | str = "auto",
    base_fontsize: float | None = None,
    dpi: int = 160,
    save_dpi: int = 600,
    transparent: bool = False,
    palette: Iterable[str] | None = None,
    grid: bool = False,
    constrained_layout: bool = True,
) -> dict[str, object]:
    """Build Matplotlib rcParams for reproducible QHE manuscript figures.

    Parameters
    ----------
    context:
        ``"paper"`` is the default compact journal setting.  The
        ``"notebook"``, ``"talk"``, and ``"poster"`` variants scale text
        and strokes while retaining the same visual language.
    use_tex:
        ``True`` forces TeX rendering, ``False`` uses Matplotlib's STIX
        mathtext, and ``"auto"`` enables TeX only when it is installed.
    """
    default_fontsize, linewidth, marker_size = _validate_context(context)
    fontsize = default_fontsize if base_fontsize is None else float(base_fontsize)
    colors = tuple(str(color) for color in (palette or QHE_LINE_PALETTE))
    if not colors:
        raise ValueError("palette must contain at least one colour.")

    return {
        # Export
        "figure.dpi": dpi,
        "savefig.dpi": save_dpi,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.035,
        "savefig.transparent": transparent,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "figure.constrained_layout.use": constrained_layout,
        # Fonts and mathematics
        "font.size": fontsize,
        "font.family": "serif",
        "font.serif": ["STIX Two Text", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "text.usetex": _resolve_usetex(use_tex),
        "axes.formatter.use_mathtext": True,
        "axes.unicode_minus": False,
        # Axes
        "axes.prop_cycle": cycler(color=colors),
        "axes.grid": grid,
        "axes.axisbelow": True,
        "axes.linewidth": 0.90,
        "axes.edgecolor": QHE_COLORS["ink"],
        "axes.labelsize": fontsize,
        "axes.labelpad": 5.0,
        "axes.titlesize": fontsize + 0.6,
        "axes.titleweight": "semibold",
        # Ticks
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "xtick.minor.visible": True,
        "ytick.minor.visible": True,
        "xtick.major.size": 5.2,
        "ytick.major.size": 5.2,
        "xtick.minor.size": 2.6,
        "ytick.minor.size": 2.6,
        "xtick.major.width": 0.90,
        "ytick.major.width": 0.90,
        "xtick.minor.width": 0.70,
        "ytick.minor.width": 0.70,
        "xtick.labelsize": fontsize - 0.5,
        "ytick.labelsize": fontsize - 0.5,
        # Lines, patches, and markers
        "lines.linewidth": linewidth,
        "lines.markersize": marker_size,
        "lines.markeredgewidth": 0.75,
        "patch.linewidth": 0.75,
        "patch.edgecolor": "white",
        "errorbar.capsize": 2.8,
        # Grids
        "grid.color": QHE_COLORS["grid"],
        "grid.linestyle": ":",
        "grid.linewidth": 0.70,
        # Legends
        "legend.frameon": True,
        "legend.framealpha": 0.96,
        "legend.facecolor": "white",
        "legend.edgecolor": "#C7CDD4",
        "legend.fancybox": False,
        "legend.fontsize": fontsize - 1.0,
        "legend.title_fontsize": fontsize - 0.4,
        # Images
        "image.cmap": "cividis",
        # Preserve editable text in common vector editors.
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }


def set_style(
    *,
    context: str = "paper",
    use_tex: bool | str = "auto",
    base_fontsize: float | None = None,
    dpi: int = 160,
    save_dpi: int = 600,
    transparent: bool = False,
    palette: Iterable[str] | None = None,
    grid: bool = False,
    constrained_layout: bool = True,
) -> None:
    """Apply the QHE figure style globally for subsequent figures."""
    # Some Matplotlib type stubs model rcParam keys as a large Literal union.
    # The dictionary is assembled dynamically, so make the compatibility cast
    # only at the Matplotlib boundary rather than weakening the public return
    # type of ``build_rcparams``.
    params = build_rcparams(
        context=context,
        use_tex=use_tex,
        base_fontsize=base_fontsize,
        dpi=dpi,
        save_dpi=save_dpi,
        transparent=transparent,
        palette=palette,
        grid=grid,
        constrained_layout=constrained_layout,
    )
    mpl.rcParams.update(cast(Any, params))


@contextmanager
def paper_style(
    *,
    context: str = "paper",
    use_tex: bool | str = "auto",
    base_fontsize: float | None = None,
    dpi: int = 160,
    save_dpi: int = 600,
    transparent: bool = False,
    palette: Iterable[str] | None = None,
    grid: bool = False,
    constrained_layout: bool = True,
):
    """Temporarily apply the QHE style inside a ``with`` block."""
    params = build_rcparams(
        context=context,
        use_tex=use_tex,
        base_fontsize=base_fontsize,
        dpi=dpi,
        save_dpi=save_dpi,
        transparent=transparent,
        palette=palette,
        grid=grid,
        constrained_layout=constrained_layout,
    )
    # See the note in ``set_style`` about Matplotlib's release-dependent
    # literal rcParam-key stubs.
    with mpl.rc_context(cast(Any, params)):
        yield


def style_axes(
    ax: Axes,
    *,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    xscale: str | None = None,
    yscale: str | None = None,
    grid: bool = True,
    grid_axis: GridAxis = "y",
    minor: bool = True,
    legend: bool = False,
    legend_loc: LegendLocation = "best",
    legend_title: str | None = None,
    legend_ncols: int = 1,
) -> Axes:
    """Finalize an axis without adding an in-plot title.

    Titles are deliberately excluded because figure captions and panel
    labels are more appropriate for the QHE manuscript.
    """
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)
    if xscale is not None:
        ax.set_xscale(xscale)
    if yscale is not None:
        ax.set_yscale(yscale)

    if minor:
        ax.minorticks_on()
    else:
        ax.minorticks_off()

    if grid:
        ax.grid(
            True,
            axis=grid_axis,
            which="major",
            linestyle=":",
            color=QHE_COLORS["grid"],
            linewidth=0.70,
        )
    else:
        ax.grid(False)

    for spine in ax.spines.values():
        spine.set_linewidth(0.90)
        spine.set_color(QHE_COLORS["ink"])

    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        top=True,
        right=True,
        length=5.2,
        width=0.90,
    )
    ax.tick_params(
        axis="both",
        which="minor",
        direction="in",
        top=True,
        right=True,
        length=2.6,
        width=0.70,
    )

    if legend:
        style_legend(
            ax,
            loc=legend_loc,
            title=legend_title,
            ncols=legend_ncols,
        )
    return ax


def style_colorbar(
    colorbar: Colorbar,
    *,
    label: str | None = None,
    minor: bool = False,
) -> Colorbar:
    """Apply the manuscript tick, font, and outline conventions to a colour bar."""
    if label is not None:
        colorbar.set_label(label, labelpad=7.0)

    # ``Colorbar.outline`` is a private Matplotlib spine subtype whose stub
    # annotation varies between releases.  The public Patch API is present at
    # runtime, and the narrow ``Any`` cast avoids a false-positive Pylance
    # error without changing behaviour.
    outline: Any = colorbar.outline
    outline.set_linewidth(0.80)
    outline.set_edgecolor(QHE_COLORS["ink"])
    colorbar.ax.tick_params(
        which="major",
        direction="in",
        length=4.0,
        width=0.80,
        labelsize=mpl.rcParams["ytick.labelsize"],
    )
    if minor:
        colorbar.minorticks_on()
        colorbar.ax.tick_params(which="minor", direction="in", length=2.0, width=0.65)
    else:
        colorbar.minorticks_off()
    return colorbar


def style_legend(
    ax: Axes,
    *,
    loc: LegendLocation = "best",
    title: str | None = None,
    ncols: int = 1,
    frameon: bool = True,
    outside: bool = False,
    above: bool = False,
) -> Legend | None:
    """Create a compact legend only when labeled artists are present.

    ``LegendLocation`` deliberately uses literal strings rather than a broad
    ``str`` annotation.  This matches the strict Matplotlib/Pylance overloads
    for :meth:`~matplotlib.axes.Axes.legend`.
    """
    handles, labels = ax.get_legend_handles_labels()
    if not handles:
        return None

    if outside and above:
        raise ValueError("outside and above cannot both be True.")

    if outside:
        legend = ax.legend(
            loc="upper left",
            title=title,
            ncols=ncols,
            frameon=frameon,
            fancybox=False,
            borderpad=0.35,
            handlelength=1.8,
            handletextpad=0.55,
            columnspacing=0.95,
            bbox_to_anchor=(1.02, 1.0),
            borderaxespad=0.0,
        )
    elif above:
        legend = ax.legend(
            loc="lower center",
            title=title,
            ncols=ncols,
            frameon=frameon,
            fancybox=False,
            borderpad=0.35,
            handlelength=1.8,
            handletextpad=0.55,
            columnspacing=0.95,
            bbox_to_anchor=(0.5, 1.02),
            borderaxespad=0.0,
        )
    else:
        legend = ax.legend(
            loc=loc,
            title=title,
            ncols=ncols,
            frameon=frameon,
            fancybox=False,
            borderpad=0.35,
            handlelength=1.8,
            handletextpad=0.55,
            columnspacing=0.95,
        )

    frame = legend.get_frame()
    frame.set_alpha(0.96)
    frame.set_edgecolor("#C7CDD4")
    frame.set_linewidth(0.75)
    return legend


def panel_label(
    ax: Axes,
    label: str,
    *,
    x: float = 0.02,
    y: float = 0.98,
    fontsize: float | None = None,
    boxed: bool = True,
) -> None:
    """Place a panel label such as ``"(a)"`` without obstructing the data."""
    bbox = None
    if boxed:
        bbox = {
            "boxstyle": "round,pad=0.16",
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.90,
        }
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontweight="bold",
        fontsize=fontsize,
        bbox=bbox,
        zorder=20,
    )


def annotate_textbox(
    ax: Axes,
    text: str,
    *,
    x: float = 0.98,
    y: float = 0.98,
    ha: Literal["left", "center", "right"] = "right",
    va: Literal["top", "center", "bottom"] = "top",
    fontsize: float | None = None,
) -> None:
    """Add a compact scientific annotation in axes coordinates."""
    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=fontsize,
        bbox={
            "boxstyle": "round,pad=0.22",
            "facecolor": "white",
            "edgecolor": "#C7CDD4",
            "linewidth": 0.70,
            "alpha": 0.94,
        },
        zorder=20,
    )


def save_figure(
    fig: Figure,
    path: str | Path,
    *,
    close: bool = False,
    dpi: int | None = None,
    facecolor: str = "white",
    formats: Sequence[str] | None = None,
) -> Path:
    """Save a figure and optional sibling formats, creating parents as needed."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi, facecolor=facecolor, bbox_inches="tight")

    if formats is not None:
        for fmt in formats:
            extension = str(fmt).lstrip(".")
            sibling = output.with_suffix(f".{extension}")
            if sibling != output:
                fig.savefig(
                    sibling,
                    dpi=dpi,
                    facecolor=facecolor,
                    bbox_inches="tight",
                )

    if close:
        plt.close(fig)
    return output


def edge_side_color(side: str, fallback: str | None = None) -> str:
    """Return a semantic colour for left or right edge-localized states."""
    key = str(side).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "left": "left_edge",
        "left_edge": "left_edge",
        "lower": "left_edge",
        "right": "right_edge",
        "right_edge": "right_edge",
        "upper": "right_edge",
    }
    return QHE_COLORS.get(aliases.get(key, ""), fallback or QHE_COLORS["muted"])


def crossing_color(orientation: int | float, fallback: str | None = None) -> str:
    """Return a semantic colour for a positively or negatively oriented crossing."""
    if orientation > 0:
        return QHE_COLORS["positive"]
    if orientation < 0:
        return QHE_COLORS["negative"]
    return fallback or QHE_COLORS["muted"]


def add_zero_line(
    ax: Axes,
    *,
    axis: Literal["x", "y"] = "y",
    linestyle: str = "--",
) -> Axes:
    """Add a subdued reference line at zero."""
    if axis == "y":
        ax.axhline(
            0.0,
            color=QHE_COLORS["reference"],
            linewidth=0.80,
            linestyle=linestyle,
            alpha=0.80,
            zorder=0,
        )
    elif axis == "x":
        ax.axvline(
            0.0,
            color=QHE_COLORS["reference"],
            linewidth=0.80,
            linestyle=linestyle,
            alpha=0.80,
            zorder=0,
        )
    else:
        raise ValueError("axis must be either 'x' or 'y'.")
    return ax
