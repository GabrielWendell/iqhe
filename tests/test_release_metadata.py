"""Release-package regression tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_metadata_check_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/check_release_metadata.py", "--tag", "v0.7.0"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PASS" in completed.stdout


def test_notebook_executor_discovers_production_notebooks() -> None:
    notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
    assert [path.name for path in notebooks] == [
        "00_conventions_and_hamiltonian_core.ipynb",
        "01_topology_reliability.ipynb",
        "02_edge_physics.ipynb",
        "03_hofstadter_bulk.ipynb",
        "04_ribbon_edge_states.ipynb",
        "05_chiral_dynamics.ipynb",
        "06_velocity_and_defect.ipynb"
    ]


def test_source_archive_excludes_git_metadata(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/create_release_archive.py",
            "--tag",
            "v0.7.0",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    archive = tmp_path / "qhe-ejp-v0.7.0-source.zip"
    checksums = tmp_path / "SHA256SUMS.txt"
    assert archive.is_file()
    assert checksums.is_file()
    with zipfile.ZipFile(archive) as bundle:
        assert not any("/.git/" in name or name.endswith("/.git") for name in bundle.namelist())
    line = checksums.read_text().strip()
    expected_hash, filename = line.split(maxsplit=1)
    assert filename == archive.name
    assert expected_hash == hashlib.sha256(archive.read_bytes()).hexdigest()


def test_generated_figure_manifest_is_machine_readable() -> None:
    manifest = ROOT / "figures" / "generated" / "main" / "manifest.json"
    if not manifest.is_file():
        return
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert "implemented_figures" in payload
