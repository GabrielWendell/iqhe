"""Create an annotated git tag after Stage 5 release checks pass.

Example:

    python scripts/create_release_tag.py --tag v0.6.0
    git push origin v0.6.0

The script never pushes by default. Pass ``--push`` only after reviewing the
local tag and confirming that the configured remote is correct.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _git(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Tag to create, e.g. v0.6.0.")
    parser.add_argument(
        "--push", action="store_true", help="Push the created tag to origin after creation."
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Permit a dirty working tree. This is discouraged for public releases.",
    )
    args = parser.parse_args()

    expected = f"v{_version()}"
    if args.tag != expected:
        print(f"Tag {args.tag!r} does not match package version {expected!r}.", file=sys.stderr)
        return 1

    metadata = subprocess.run(
        [sys.executable, "scripts/check_release_metadata.py", "--tag", args.tag],
        cwd=ROOT,
        check=False,
    )
    if metadata.returncode != 0:
        return metadata.returncode

    status = _git("status", "--porcelain")
    if status.returncode != 0:
        print(status.stderr, file=sys.stderr, end="")
        return status.returncode
    if status.stdout.strip() and not args.allow_dirty:
        print(
            "Refusing to tag a dirty working tree. Commit or stash changes first.", file=sys.stderr
        )
        return 1

    existing = _git("tag", "--list", args.tag)
    if existing.returncode != 0:
        print(existing.stderr, file=sys.stderr, end="")
        return existing.returncode
    if existing.stdout.strip():
        print(f"Tag {args.tag!r} already exists.", file=sys.stderr)
        return 1

    created = _git("tag", "-a", args.tag, "-m", f"IQHE {args.tag} release")
    if created.returncode != 0:
        print(created.stderr, file=sys.stderr, end="")
        return created.returncode
    print(f"Created annotated tag {args.tag}.")

    if args.push:
        pushed = _git("push", "origin", args.tag)
        if pushed.returncode != 0:
            print(pushed.stderr, file=sys.stderr, end="")
            return pushed.returncode
        print(f"Pushed {args.tag} to origin.")
    else:
        print(f"Review locally, then publish with: git push origin {args.tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
