# Environment and installation

## Supported Python versions

QHE-EJP `0.6.0` supports Python 3.11 through 3.13. The canonical Conda environment targets Python
3.11 for a conservative teaching/release baseline.

## Installation routes

### Conda or Mamba

```bash
conda env create -f environment.yml
conda activate qhe
python scripts/run_release_smoke.py
```

### Virtual environment and pip

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev,notebooks,release]"
python scripts/run_release_smoke.py
```

The editable install is intentional: notebooks, scripts, and tests exercise the same source tree that a
contributor edits.

## Version information and snapshots

- `pyproject.toml` specifies supported dependency ranges and optional release extras.
- `environment.yml` is the canonical Conda/Mamba specification.
- `requirements/release-environment-py313.txt` records the exact direct-package snapshot used to
  validate this release bundle in the Stage 5 build environment.
- `scripts/export_environment_snapshot.py` writes a new exact snapshot for a user's own platform.

The supplied snapshot is a documented platform-specific record, not a claim of a universal binary lock:
compiled scientific packages have platform- and Python-version-specific wheels. For a new public release,
store the regenerated snapshot alongside the tagged code and the GitHub Actions run URL.

## Clean-install acceptance procedure

The release workflow performs the following in a fresh checkout:

1. installs `.[dev,notebooks,release]`;
2. runs structural verification and all Stage 1–4 checks;
3. runs the complete test suite;
4. executes every production teaching notebook in a non-interactive kernel;
5. rebuilds manuscript Figures 1–6 from source scripts;
6. builds and checks sdist/wheel distribution artifacts.

Use `python scripts/run_release_smoke.py` locally after installation to run the same scientific
acceptance chain, excluding remote dependency resolution and GitHub-release publication.
