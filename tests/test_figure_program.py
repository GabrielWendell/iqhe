"""Regression tests for the Stage-4 figure programme."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from qhe.viz import plot_conceptual_roadmap, plot_fhs_plaquette

ROOT = Path(__file__).resolve().parents[1]


def test_vector_schematics_are_title_free() -> None:
    for builder in (plot_conceptual_roadmap, plot_fhs_plaquette):
        figure, _ = builder(apply_style=True)
        try:
            assert all(not axis.get_title() for axis in figure.axes)
        finally:
            figure.clear()


def test_stage4_figure_program_has_source_captions_and_future_register() -> None:
    manifest = (ROOT / "figures" / "FIGURE_MANIFEST.md").read_text()
    captions = (ROOT / "figures" / "captions.md").read_text()
    for index in range(1, 7):
        assert f"figure_{index:02d}_" in manifest
        assert f"## Figure {index}" in captions
    assert "figure_07_chiral_dynamics" in manifest
    assert "figure_08_velocity_and_defect" in manifest


def test_fast_renderer_exports_complete_contract(tmp_path: Path) -> None:
    output_directory = tmp_path / "main"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_main_figures.py",
            "--fast",
            "--output-dir",
            str(output_directory),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    document = json.loads((output_directory / "manifest.json").read_text())
    records = document["implemented_figures"]
    assert len(records) == 6
    for record in records:
        assert record["title_free"] is True
        assert any(filename.endswith(".pdf") for filename in record["files"])
        assert any(filename.endswith(".png") for filename in record["files"])
        for filename in record["files"]:
            assert (output_directory / filename).stat().st_size > 1024
