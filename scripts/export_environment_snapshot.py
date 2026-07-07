"""Write a direct-dependency environment snapshot for a future release.

The output is intentionally a transparent platform-specific record rather
than a misleading universal binary lock. Use it alongside ``environment.yml``
and the GitHub Actions run associated with a release tag.
"""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    "numpy",
    "scipy",
    "matplotlib",
    "sympy",
    "pandas",
    "jupyterlab",
    "ipykernel",
    "nbformat",
    "nbclient",
    "nbconvert",
    "pytest",
    "pytest-cov",
    "ruff",
    "build",
    "twine",
    "pip",
    "setuptools",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "requirements" / "release-environment-local.txt",
    )
    args = parser.parse_args()

    lines = [
        "# QHE-EJP direct-dependency environment snapshot",
        f"# Generated at {datetime.now(UTC).isoformat()}",
        f"# Python: {sys.version.split()[0]}",
        f"# Platform: {platform.platform()}",
        "# This is a platform-specific release record, not a universal binary lock.",
        "",
    ]
    for package in PACKAGES:
        try:
            lines.append(f"{package}=={metadata.version(package)}")
        except metadata.PackageNotFoundError:
            lines.append(f"# {package}: not installed in this environment")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Environment snapshot written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
