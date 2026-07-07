"""Render the Stage-4 EJP manuscript figure programme deterministically.

Run from the repository root:

    python scripts/make_main_figures.py

The command regenerates every currently implemented main figure without
notebook state or manual editing. It exports vector PDF, high-resolution PNG,
and a machine-readable manifest in the requested output directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure, SubFigure

from qhe.boundary import analyze_bulk_boundary_correspondence
from qhe.models import DiracParameters, HarperHofstadterParameters
from qhe.topology import analyze_harper_hofstadter_topology, harper_hofstadter_convergence
from qhe.viz import (
    plot_conceptual_roadmap,
    plot_fhs_kubo_validation,
    plot_fhs_plaquette,
    plot_hofstadter_bulk_bands,
    plot_massive_dirac_warmup,
    plot_ribbon_bulk_boundary_figure,
)
from qhe.viz.style import save_figure, set_style

DEFAULT_CONFIG_PATH = ROOT / "configs" / "figure_program_phi_1_3.toml"


PaperContext = Literal["paper", "notebook", "talk", "poster"]
FigureLike = Figure | SubFigure
_PAPER_CONTEXTS: tuple[PaperContext, ...] = ("paper", "notebook", "talk", "poster")


def _parse_paper_context(value: object) -> PaperContext:
    """Validate and narrow a TOML context value to the plotting API contract."""
    context = str(value).strip().lower()
    if context not in _PAPER_CONTEXTS:
        valid = ", ".join(_PAPER_CONTEXTS)
        raise ValueError(f"Unsupported figure context {context!r}. Choose one of: {valid}.")
    return cast(PaperContext, context)


def _root_figure(figure: FigureLike) -> Figure:
    """Return the owning Matplotlib Figure for a Figure or a nested SubFigure.

    Plot constructors accept optional pre-existing axes and therefore expose
    ``Figure | SubFigure`` in their public return annotations.  Files must be
    exported through the owning top-level ``Figure``.
    """
    if isinstance(figure, Figure):
        return figure
    return cast(Figure, figure.figure)


@dataclass(frozen=True, slots=True)
class FigureBuildConfig:
    """Resolved parameters required by the deterministic Stage-4 figure build."""

    model: HarperHofstadterParameters
    dirac: DiracParameters
    dirac_kmax: float
    dirac_n_line: int
    dirac_n_map: int
    topology_nkx: int
    topology_nky: int
    band_index: int
    convergence_mesh_sizes: tuple[int, ...]
    ribbon_lx: int
    ribbon_nky: int
    edge_width: int
    edge_participation_threshold: float
    side_margin: float
    context: PaperContext
    formats: tuple[str, ...]
    output_directory: Path

    def as_manifest_dict(self) -> dict[str, Any]:
        return {
            "model": {
                "p": self.model.p,
                "q": self.model.q,
                "tx": self.model.tx,
                "ty": self.model.ty,
                "lattice_spacing": self.model.lattice_spacing,
            },
            "dirac": {
                "v_fermi": self.dirac.v_fermi,
                "mass": self.dirac.mass,
                "kmax": self.dirac_kmax,
                "n_line": self.dirac_n_line,
                "n_map": self.dirac_n_map,
            },
            "topology": {
                "nkx": self.topology_nkx,
                "nky": self.topology_nky,
                "band_index": self.band_index,
                "convergence_mesh_sizes": list(self.convergence_mesh_sizes),
            },
            "ribbon": {
                "lx": self.ribbon_lx,
                "nky": self.ribbon_nky,
                "edge_width": self.edge_width,
                "edge_participation_threshold": self.edge_participation_threshold,
                "side_margin": self.side_margin,
            },
            "build": {
                "context": self.context,
                "formats": list(self.formats),
                "output_directory": str(self.output_directory),
            },
        }


def _read_config(path: Path, output_directory: Path | None = None) -> FigureBuildConfig:
    with path.open("rb") as handle:
        document = tomllib.load(handle)
    model_doc = document["model"]
    dirac_doc = document["dirac"]
    topology_doc = document["topology"]
    ribbon_doc = document["ribbon"]
    build_doc = document["build"]
    resolved_output = output_directory or ROOT / str(build_doc["output_directory"])
    return FigureBuildConfig(
        model=HarperHofstadterParameters(
            p=int(model_doc["p"]),
            q=int(model_doc["q"]),
            tx=float(model_doc["tx"]),
            ty=float(model_doc["ty"]),
            lattice_spacing=float(model_doc["lattice_spacing"]),
        ),
        dirac=DiracParameters(
            v_fermi=float(dirac_doc["v_fermi"]),
            mass=float(dirac_doc["mass"]),
        ),
        dirac_kmax=float(dirac_doc["kmax"]),
        dirac_n_line=int(dirac_doc["n_line"]),
        dirac_n_map=int(dirac_doc["n_map"]),
        topology_nkx=int(topology_doc["nkx"]),
        topology_nky=int(topology_doc["nky"]),
        band_index=int(topology_doc["band_index"]),
        convergence_mesh_sizes=tuple(
            int(value) for value in topology_doc["convergence_mesh_sizes"]
        ),
        ribbon_lx=int(ribbon_doc["lx"]),
        ribbon_nky=int(ribbon_doc["nky"]),
        edge_width=int(ribbon_doc["edge_width"]),
        edge_participation_threshold=float(ribbon_doc["edge_participation_threshold"]),
        side_margin=float(ribbon_doc["side_margin"]),
        context=_parse_paper_context(build_doc["context"]),
        formats=tuple(str(value).lstrip(".") for value in build_doc["formats"]),
        output_directory=resolved_output,
    )


def _fast_config(config: FigureBuildConfig) -> FigureBuildConfig:
    """Return a small deterministic smoke-render configuration for CI and tests."""
    return FigureBuildConfig(
        model=config.model,
        dirac=config.dirac,
        dirac_kmax=config.dirac_kmax,
        dirac_n_line=min(config.dirac_n_line, 101),
        dirac_n_map=min(config.dirac_n_map, 61),
        topology_nkx=min(config.topology_nkx, 25),
        topology_nky=min(config.topology_nky, 25),
        band_index=config.band_index,
        convergence_mesh_sizes=tuple(sorted({15, 25, 35})),
        ribbon_lx=min(config.ribbon_lx, 36),
        ribbon_nky=min(config.ribbon_nky, 121),
        edge_width=config.edge_width,
        edge_participation_threshold=config.edge_participation_threshold,
        side_margin=config.side_margin,
        context=config.context,
        formats=config.formats,
        output_directory=config.output_directory,
    )


def _git_revision() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def _assert_no_axes_titles(figure: Figure, figure_id: str) -> None:
    titles = [axis.get_title() for axis in figure.axes if axis.get_title().strip()]
    if titles:
        joined = "; ".join(titles)
        raise RuntimeError(f"{figure_id} violates the no-title policy: {joined}")


def _render_and_record(
    figure_id: str,
    figure: FigureLike,
    *,
    output_directory: Path,
    formats: Iterable[str],
) -> dict[str, Any]:
    root_figure = _root_figure(figure)
    _assert_no_axes_titles(root_figure, figure_id)
    output_path = output_directory / f"{figure_id}.pdf"
    primary = save_figure(root_figure, output_path, formats=tuple(formats), close=True)
    files = sorted({primary.name, *(output_path.with_suffix(f".{fmt}").name for fmt in formats)})
    return {
        "id": figure_id,
        "files": files,
        "title_free": True,
    }


def render_main_figures(config: FigureBuildConfig) -> dict[str, Any]:
    """Render every currently implemented static manuscript figure.

    The calculation intentionally reuses shared topology and ribbon analyses
    so that the plotted figures and the machine-readable build manifest refer
    to the same frozen model and numerical parameters.
    """
    config.output_directory.mkdir(parents=True, exist_ok=True)
    set_style(context=config.context, use_tex=False, grid=False, constrained_layout=True)

    topology = analyze_harper_hofstadter_topology(
        config.model,
        nkx=config.topology_nkx,
        nky=config.topology_nky,
    )
    convergence = harper_hofstadter_convergence(
        config.model,
        mesh_sizes=config.convergence_mesh_sizes,
    )
    edge_analysis = analyze_bulk_boundary_correspondence(
        config.model,
        bulk_nkx=config.topology_nkx,
        bulk_nky=config.topology_nky,
        ribbon_lx=config.ribbon_lx,
        ribbon_nky=config.ribbon_nky,
        edge_width=config.edge_width,
        edge_threshold=config.edge_participation_threshold,
        side_margin=config.side_margin,
    )

    records: list[dict[str, Any]] = []
    figure, _ = plot_conceptual_roadmap(context=config.context, apply_style=False)
    records.append(
        _render_and_record(
            "figure_01_conceptual_roadmap",
            figure,
            output_directory=config.output_directory,
            formats=config.formats,
        )
    )

    figure, _ = plot_fhs_plaquette(context=config.context, apply_style=False)
    records.append(
        _render_and_record(
            "figure_02_fhs_plaquette",
            figure,
            output_directory=config.output_directory,
            formats=config.formats,
        )
    )

    figure, _ = plot_massive_dirac_warmup(
        config.dirac,
        kmax=config.dirac_kmax,
        n_line=config.dirac_n_line,
        n_map=config.dirac_n_map,
        context=config.context,
        apply_style=False,
    )
    records.append(
        _render_and_record(
            "figure_03_massive_dirac_warmup",
            figure,
            output_directory=config.output_directory,
            formats=config.formats,
        )
    )

    figure, _ = plot_hofstadter_bulk_bands(
        topology,
        config.model,
        context=config.context,
        apply_style=False,
        legend_bbox_to_anchor=(0.45, 0.55),
    )
    records.append(
        _render_and_record(
            "figure_04_hofstadter_bulk_bands",
            figure,
            output_directory=config.output_directory,
            formats=config.formats,
        )
    )

    figure, _ = plot_fhs_kubo_validation(
        topology,
        convergence,
        band_index=config.band_index,
        context=config.context,
        apply_style=False,
    )
    records.append(
        _render_and_record(
            "figure_05_fhs_kubo_validation",
            figure,
            output_directory=config.output_directory,
            formats=config.formats,
        )
    )

    figure, _ = plot_ribbon_bulk_boundary_figure(
        edge_analysis,
        context=config.context,
        apply_style=False,
    )
    records.append(
        _render_and_record(
            "figure_06_ribbon_bulk_boundary",
            figure,
            output_directory=config.output_directory,
            formats=config.formats,
        )
    )

    generated_files = [
        config.output_directory / name for record in records for name in record["files"]
    ]
    manifest: dict[str, Any] = {
        "stage": 4,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_revision": _git_revision(),
        "python": sys.version,
        "platform": sys.platform,
        "config": config.as_manifest_dict(),
        "implemented_figures": records,
        "reserved_for_later_stages": [
            "figure_07_chiral_dynamics",
            "figure_08_velocity_and_defect",
        ],
        "files": {
            str(path.name): {"sha256": _sha256(path), "bytes": path.stat().st_size}
            for path in generated_files
        },
    }
    manifest_path = config.output_directory / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the Stage-4 figure-program TOML configuration.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory receiving generated figures and manifest.json.",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use a small smoke-render configuration for CI or development checks.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    config_path = arguments.config.resolve()
    output_directory = arguments.output_dir.resolve() if arguments.output_dir else None
    config = _read_config(config_path, output_directory=output_directory)
    if arguments.fast:
        config = _fast_config(config)
    manifest = render_main_figures(config)
    print("Stage-4 figure build complete")
    print(f"Output directory: {config.output_directory}")
    print("Rendered figures:")
    for record in manifest["implemented_figures"]:
        print(f"  - {record['id']}: {', '.join(record['files'])}")
    print(f"Manifest: {config.output_directory / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
