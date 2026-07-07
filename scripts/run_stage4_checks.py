"""Run the Stage-4 clean-render acceptance checks.

Run from the repository root:

    python scripts/run_stage4_checks.py

The script builds every currently implemented figure into a fresh temporary
directory using the smoke configuration, validates the PDF/PNG/manifest
contract, verifies captions and figure-manifest coverage, and reports the
clean-render result.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    "figure_01_conceptual_roadmap",
    "figure_02_fhs_plaquette",
    "figure_03_massive_dirac_warmup",
    "figure_04_hofstadter_bulk_bands",
    "figure_05_fhs_kubo_validation",
    "figure_06_ribbon_bulk_boundary",
)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="qhe-stage4-") as temporary:
        output = Path(temporary) / "figures"
        command = [
            sys.executable,
            "scripts/make_main_figures.py",
            "--fast",
            "--output-dir",
            str(output),
        ]
        environment = dict(**__import__("os").environ)
        environment["PYTHONPATH"] = (
            str(ROOT / "src") + __import__("os").pathsep + environment.get("PYTHONPATH", "")
        )
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        print(completed.stdout, end="")
        if completed.returncode != 0:
            print(completed.stderr, file=sys.stderr, end="")
            return completed.returncode

        manifest_path = output / "manifest.json"
        if not manifest_path.is_file():
            failures.append("The figure renderer did not create manifest.json.")
        else:
            manifest = json.loads(manifest_path.read_text())
            received = tuple(record["id"] for record in manifest.get("implemented_figures", []))
            if received != EXPECTED:
                failures.append(
                    "Manifest figure IDs do not match the frozen Stage-4 programme: "
                    f"received {received!r}."
                )
            for record in manifest.get("implemented_figures", []):
                if record.get("title_free") is not True:
                    failures.append(
                        f"{record.get('id')} is not marked title-free in the manifest."
                    )
                for filename in record.get("files", []):
                    candidate = output / filename
                    if not candidate.is_file() or candidate.stat().st_size <= 1024:
                        failures.append(
                            f"Missing or implausibly small generated output: {candidate.name}."
                        )
            if tuple(manifest.get("reserved_for_later_stages", [])) != (
                "figure_07_chiral_dynamics",
                "figure_08_velocity_and_defect",
            ):
                failures.append("Future dynamics figures are not registered as reserved outputs.")

    captions = (ROOT / "figures" / "captions.md").read_text()
    figure_manifest = (ROOT / "figures" / "FIGURE_MANIFEST.md").read_text()
    for number, figure_id in enumerate(EXPECTED, start=1):
        if f"## Figure {number}" not in captions:
            failures.append(f"Caption source lacks Figure {number}.")
        if figure_id not in figure_manifest:
            failures.append(f"Figure manifest lacks {figure_id}.")

    if failures:
        print("Stage-4 checks failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("Stage-4 clean figure-render acceptance checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
