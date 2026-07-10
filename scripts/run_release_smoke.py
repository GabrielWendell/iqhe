"""Run the release acceptance workflow after installation.

Run from the repository root:

    python scripts/run_release_smoke.py

This is the local counterpart to the clean-checkout CI workflow. It assumes
that the current environment already has ``.[dev,notebooks,release]``
installed. It does not perform network access or publish a GitHub release.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory for executed notebooks and fast-rendered figures. "
            "Defaults to a temporary directory."
        ),
    )
    parser.add_argument(
        "--skip-notebooks",
        action="store_true",
        help="Skip non-interactive notebook execution (not allowed in release CI).",
    )
    parser.add_argument(
        "--skip-figures",
        action="store_true",
        help="Skip the clean fast figure render (not allowed in release CI).",
    )
    return parser.parse_args()


def _run(command: list[str], environment: dict[str, str]) -> None:
    print("+", " ".join(command))
    completed = subprocess.run(command, cwd=ROOT, env=environment, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {completed.returncode}: {' '.join(command)}"
        )


def main() -> int:
    args = _parse_args()
    environment = dict(os.environ)
    environment["MPLBACKEND"] = "Agg"
    environment["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + environment.get("PYTHONPATH", "")

    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.output_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="qhe-release-smoke-")
        output_dir = Path(temporary.name)
    else:
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    try:
        _run([sys.executable, "scripts/check_release_metadata.py", "--tag", "v0.7.0"], environment)
        _run([sys.executable, "scripts/verify_repo.py"], environment)
        _run([sys.executable, "scripts/run_stage1_checks.py"], environment)
        _run([sys.executable, "scripts/run_stage2_checks.py"], environment)
        _run([sys.executable, "scripts/run_stage3_checks.py"], environment)
        _run([sys.executable, "scripts/run_stage4_checks.py"], environment)
        _run([sys.executable, "scripts/run_stage6_checks.py"], environment)
        _run([sys.executable, "-m", "pytest", "-q"], environment)

        if not args.skip_notebooks:
            _run(
                [
                    sys.executable,
                    "scripts/execute_notebooks.py",
                    "--output-dir",
                    str(output_dir / "notebooks"),
                ],
                environment,
            )
        if not args.skip_figures:
            _run(
                [
                    sys.executable,
                    "scripts/make_main_figures.py",
                    "--fast",
                    "--output-dir",
                    str(output_dir / "figures"),
                ],
                environment,
            )
    except RuntimeError as exc:
        print(f"Release smoke test failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if temporary is not None:
            temporary.cleanup()

    print("Release smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
