"""Execute all production teaching notebooks without relying on notebook state.

Run from the repository root:

    python scripts/execute_notebooks.py

Executed copies are written to ``results/generated/notebooks`` by default. The
source notebooks are never modified. The executor uses the active Python
kernel, so a clean editable installation is sufficient; users do not need to
manually create a kernel named ``qhe``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIRECTORY = ROOT / "notebooks"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "generated" / "notebooks",
        help="Directory for executed copies and execution manifest.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Per-notebook execution timeout in seconds.",
    )
    parser.add_argument(
        "--pattern",
        default="*.ipynb",
        help="Glob pattern evaluated inside notebooks/ (default: *.ipynb).",
    )
    return parser.parse_args()


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = _parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    notebooks = sorted(NOTEBOOK_DIRECTORY.glob(args.pattern))
    if not notebooks:
        print("No production notebooks matched the requested pattern.", file=sys.stderr)
        return 1

    environment = dict(os.environ)
    environment["MPLBACKEND"] = "Agg"
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + existing_pythonpath

    records: list[dict[str, object]] = []
    for source in notebooks:
        print(f"Executing {source.relative_to(ROOT)} ...")
        notebook = nbformat.read(source, as_version=4)
        notebook.metadata.setdefault("kernelspec", {})["name"] = "python3"
        client = NotebookClient(
            notebook,
            timeout=args.timeout,
            kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
            allow_errors=False,
        )
        try:
            client.execute(env=environment)
        except Exception as exc:  # pragma: no cover - exercised by release smoke failures.
            print(f"Notebook execution failed: {source.name}: {exc}", file=sys.stderr)
            return 1

        destination = output_dir / source.name
        nbformat.write(notebook, destination)
        records.append(
            {
                "source": str(source.relative_to(ROOT)),
                "output": str(destination.relative_to(ROOT))
                if destination.is_relative_to(ROOT)
                else str(destination),
                "sha256_source": _digest(source),
                "sha256_executed": _digest(destination),
            }
        )

    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "python_executable": sys.executable,
        "notebooks": records,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Executed {len(records)} notebook(s). Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
