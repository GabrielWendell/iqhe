"""Create a portable source archive for a semantic QHE-EJP release tag.

The archive excludes Git metadata, caches, local environments, and transient
build directories while retaining source code, notebooks, configurations,
documentation, generated reference figures, and release metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    "ENV",
    "build",
    "dist",
    "release-assets",
    "ci-artifacts",
    "release-smoke",
    "__pycache__",
    ".ipynb_checkpoints",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Semantic tag, e.g. v0.6.0.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "release-assets",
        help="Directory receiving the source archive and checksum manifest.",
    )
    return parser.parse_args()


def _validate_tag(tag: str) -> None:
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:[A-Za-z0-9.-]+)?", tag):
        raise ValueError(f"Release tag {tag!r} is not semantic (expected vX.Y.Z).")


def _should_include(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    if relative.parts[:2] == ("results", "generated"):
        return False
    return path.suffix not in EXCLUDED_SUFFIXES


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = _parse_args()
    try:
        _validate_tag(args.tag)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"qhe-ejp-{args.tag}-source.zip"
    root_name = f"qhe-ejp-{args.tag}"

    with zipfile.ZipFile(
        archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as bundle:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or not _should_include(path):
                continue
            relative = path.relative_to(ROOT)
            bundle.write(path, Path(root_name) / relative)

    checksums = output_dir / "SHA256SUMS.txt"
    checksums.write_text(f"{_sha256(archive)}  {archive.name}\n", encoding="utf-8")
    print(f"Release source archive: {archive}")
    print(f"SHA-256 manifest: {checksums}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
