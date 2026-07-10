"""Render Stage-6 dynamics manuscript figures in an isolated process."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Literal, TypedDict, cast

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure

from qhe.dynamics import DynamicsConfig, analyze_chiral_dynamics
from qhe.models import HarperHofstadterParameters
from qhe.viz import plot_chiral_dynamics_figure, plot_velocity_defect_figure
from qhe.viz.style import set_style

PaperContext = Literal["paper", "notebook", "talk", "poster"]
GapSelector = Literal[0, 1]
EdgeSide = Literal["left", "right", "bottom", "top"]


class FigureRecord(TypedDict):
    """Manifest entry produced for each rendered Stage-6 figure."""

    id: str
    files: list[str]
    title_free: bool


DEFAULT_CONFIG = ROOT / "configs" / "figure_program_phi_1_3.toml"
_CONTEXTS: tuple[PaperContext, ...] = ("paper", "notebook", "talk", "poster")
_GAP_SELECTORS: tuple[GapSelector, ...] = (0, 1)
_EDGE_SIDES: tuple[EdgeSide, ...] = ("left", "right", "bottom", "top")


def _context(value: object) -> PaperContext:
    text = str(value).strip().lower()
    if text not in _CONTEXTS:
        raise ValueError(f"Unsupported context: {text!r}.")
    return cast(PaperContext, text)


def _gap_selector(value: object) -> GapSelector:
    """Parse and narrow a TOML value to a valid Stage-6 bulk-gap selector."""
    if isinstance(value, bool):
        raise TypeError("gap_index must be an integer selector, not a boolean.")
    if isinstance(value, int):
        gap_index = value
    elif isinstance(value, str):
        gap_index = int(value.strip())
    else:
        raise TypeError(
            f"gap_index must be an integer or integer-like string; got {type(value).__name__}."
        )

    if gap_index not in _GAP_SELECTORS:
        valid = ", ".join(str(item) for item in _GAP_SELECTORS)
        raise ValueError(f"Unsupported gap_index {gap_index!r}; expected one of: {valid}.")
    return cast(GapSelector, gap_index)


def _edge_side(value: object) -> EdgeSide:
    side = str(value).strip().lower()
    if side not in _EDGE_SIDES:
        valid = ", ".join(_EDGE_SIDES)
        raise ValueError(f"Unsupported side {side!r}; expected one of: {valid}.")
    return cast(EdgeSide, side)


def _config(path: Path) -> tuple[DynamicsConfig, PaperContext, tuple[str, ...]]:
    with path.open("rb") as handle:
        document = tomllib.load(handle)
    model = document["model"]
    dynamics = document["dynamics"]
    build = document["build"]
    params = HarperHofstadterParameters(
        p=int(model["p"]),
        q=int(model["q"]),
        tx=float(model["tx"]),
        ty=float(model["ty"]),
        lattice_spacing=float(model["lattice_spacing"]),
    )
    return (
        DynamicsConfig(
            parameters=params,
            gap_index=_gap_selector(dynamics.get("gap_index", 0)),
            side=_edge_side(dynamics.get("side", "left")),
            lx=int(dynamics.get("lx", 12)),
            ly=int(dynamics.get("ly", 30)),
            edge_width=int(dynamics.get("edge_width", 2)),
            sigma_transverse=float(dynamics.get("sigma_transverse", 0.8)),
            sigma_longitudinal=float(dynamics.get("sigma_longitudinal", 5.0)),
            center_longitudinal=float(dynamics.get("center_longitudinal", 0.5)),
            offset_from_boundary=float(dynamics.get("offset_from_boundary", 0.5)),
            time_final=float(dynamics.get("time_final", 4.0)),
            n_times=int(dynamics.get("n_times", 41)),
            fit_until=float(dynamics.get("fit_until", 2.0)),
            minimum_side_participation=float(dynamics.get("minimum_side_participation", 0.20)),
            bulk_nkx=int(dynamics.get("bulk_nkx", 15)),
            ribbon_lx=int(dynamics.get("ribbon_lx", 24)),
            ribbon_nky=int(dynamics.get("ribbon_nky", 81)),
            ribbon_edge_threshold=float(dynamics.get("ribbon_edge_threshold", 0.50)),
            defect_factor=float(dynamics.get("defect_factor", 0.0)),
            hbar=float(dynamics.get("hbar", 1.0)),
        ),
        _context(build.get("context", "paper")),
        tuple(str(value).lstrip(".") for value in build.get("formats", ["pdf", "png"])),
    )


def _assert_title_free(figure: Figure, figure_id: str) -> None:
    titles = [axis.get_title() for axis in figure.axes if axis.get_title().strip()]
    if titles:
        raise RuntimeError(f"{figure_id} violates the no-title policy: {titles!r}")


def _save(figure_id: str, figure: Figure, output_dir: Path, formats: tuple[str, ...]) -> FigureRecord:
    _assert_title_free(figure, figure_id)
    import matplotlib.pyplot as plt

    files: list[str] = []
    png_path = output_dir / f"{figure_id}.png"
    figure.savefig(png_path, dpi=220, facecolor="white")
    files.append(png_path.name)

    if "pdf" in {str(fmt).lstrip(".") for fmt in formats}:
        from PIL import Image

        pdf_path = output_dir / f"{figure_id}.pdf"
        with Image.open(png_path) as image:
            image.convert("RGB").save(pdf_path, "PDF", resolution=220.0)
        files.append(pdf_path.name)

    plt.close(figure)
    return {"id": figure_id, "files": sorted(set(files)), "title_free": True}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config, context, formats = _config(args.config.resolve())
    set_style(context=context, use_tex=False, grid=False, constrained_layout=True)
    analysis = analyze_chiral_dynamics(config)
    records: list[FigureRecord] = []
    figure, _ = plot_chiral_dynamics_figure(analysis, context=context, apply_style=False)
    records.append(_save("figure_07_chiral_dynamics", figure, output_dir, formats))
    figure, _ = plot_velocity_defect_figure(analysis, context=context, apply_style=False)
    records.append(_save("figure_08_velocity_and_defect", figure, output_dir, formats))
    (output_dir / "stage6_manifest.json").write_text(
        json.dumps({"stage": 6, "implemented_figures": records}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Stage-6 dynamics figures rendered:")
    for record in records:
        print(f"  - {record['id']}: {', '.join(record['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
