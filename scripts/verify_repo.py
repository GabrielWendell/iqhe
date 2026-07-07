"""Verify the Stage-0 repository scaffold without requiring project installation.

Run from the repository root:

    python scripts/verify_repo.py
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "pyproject.toml",
    "environment.yml",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "docs/PROJECT_SCOPE.md",
    "docs/REPRODUCIBILITY.md",
    "docs/DECISION_LOG.md",
    "docs/CONVENTIONS.md",
    "docs/ARCHITECTURE.md",
    "docs/STAGE_0.md",
    "docs/REFERENCE_MATERIALS.md",
    "src/qhe/__init__.py",
    "src/qhe/validation/basic.py",
    "tests/test_package.py",
    "tests/test_validation.py",
    "legacy/Efeito_Hall_Quantico.ipynb",
    "legacy/LEGACY_MANIFEST.md",
)


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
    if missing:
        print("Missing required Stage-0 paths:")
        for path in missing:
            print(f"  - {path}")
        return 1

    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)

    package = project.get("project", {})
    expected_name = "qhe"
    if package.get("name") != expected_name:
        print(f"Unexpected project name: {package.get('name')!r} (expected {expected_name!r})")
        return 1
    version = package.get("version")
    if not isinstance(version, str) or re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        print(
            f"Package version must use the release form MAJOR.MINOR.PATCH; received {version!r}."
        )
        return 1

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    for required_key in ("cff-version:", "title:", "version:", "repository-code:"):
        if required_key not in citation:
            print(f"CITATION.cff is missing required key: {required_key}")
            return 1

    print("Stage-0 repository scaffold is structurally valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
