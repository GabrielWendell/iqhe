"""Validate release-facing metadata without external dependencies.

Run from the repository root:

    python scripts/check_release_metadata.py --tag v0.7.0

The check is deliberately conservative: it confirms version synchronization,
public repository URLs, essential release documentation, and the frozen legacy
notebook hash. It does not claim that a DOI exists.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_NOTEBOOK = ROOT / "legacy" / "Efeito_Hall_Quantico.ipynb"
LEGACY_SHA256 = "271bef33cc8fa80fdf988c344e56fae59e885ee695a634230a5a69dea5de4d03"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tag",
        default=None,
        help="Optional semantic release tag to compare against the package version, e.g. v0.7.0.",
    )
    return parser.parse_args()


def _version_from_meta() -> str:
    namespace: dict[str, object] = {}
    path = ROOT / "src" / "qhe" / "_meta.py"
    exec(path.read_text(encoding="utf-8"), namespace)
    version = namespace.get("__version__")
    if not isinstance(version, str):
        raise RuntimeError("src/qhe/_meta.py does not define a string __version__.")
    return version


def _version_from_citation() -> str | None:
    match = re.search(
        r"^version:\s*([^\s]+)\s*$", (ROOT / "CITATION.cff").read_text(), re.MULTILINE
    )
    return match.group(1) if match else None


def _legacy_hash() -> str:
    hasher = hashlib.sha256()
    with LEGACY_NOTEBOOK.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> int:
    args = _parse_args()
    failures: list[str] = []

    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    package_version = str(project["version"])
    module_version = _version_from_meta()
    citation_version = _version_from_citation()

    versions = {
        "pyproject.toml": package_version,
        "qhe.__version__": module_version,
        "CITATION.cff": citation_version,
    }
    if len(set(versions.values())) != 1:
        failures.append(f"Version metadata are inconsistent: {versions!r}.")

    if args.tag is not None and args.tag != f"v{package_version}":
        message = (
            f"Requested release tag {args.tag!r} does not match package version "
            f"v{package_version}."
        )
        failures.append(message)

    urls = project.get("urls", {})
    for name in ("Homepage", "Repository", "Issues"):
        value = str(urls.get(name, ""))
        if "github.com/GabrielWendell/qhe-ejp" not in value:
            failures.append(f"Project URL {name!r} is missing or not public-facing: {value!r}.")

    release_paths = (
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "CHANGELOG.md",
        "MANIFEST.in",
        "environment.yml",
        "docs/DATA_AVAILABILITY.md",
        "docs/ENVIRONMENT.md",
        "docs/RELEASE.md",
        "docs/STAGE_5.md",
        "release/RELEASE_CHECKLIST.md",
        f"release/RELEASE_NOTES_v{package_version}.md",
        "requirements/release-environment-py313.txt",
        "scripts/execute_notebooks.py",
        "scripts/run_release_smoke.py",
        "scripts/create_release_archive.py",
        "scripts/create_release_tag.py",
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
    )
    for relative in release_paths:
        if not (ROOT / relative).is_file():
            failures.append(f"Required release path is missing: {relative}.")

    text_paths = (ROOT / "README.md", ROOT / "CITATION.cff", ROOT / "docs" / "RELEASE.md")
    for path in text_paths:
        if "REPLACE-WITH-ACCOUNT" in path.read_text(encoding="utf-8"):
            failures.append(f"Placeholder repository URL remains in {path.relative_to(ROOT)}.")

    if not LEGACY_NOTEBOOK.is_file():
        failures.append("Frozen legacy notebook is missing.")
    elif _legacy_hash() != LEGACY_SHA256:
        failures.append("Frozen legacy notebook SHA-256 does not match the provenance manifest.")

    if failures:
        print("Release metadata checks failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"Release metadata checks: PASS (v{package_version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
