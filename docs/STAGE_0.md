# Stage 0 implementation record

## Objective

Establish a clean, reproducible repository foundation before rebuilding the physics implementation.

## Delivered

- installable `src/`-layout Python package;
- package metadata and dependency declaration in `pyproject.toml`;
- Conda/Mamba environment in `environment.yml`;
- unit-test and lint configuration;
- Git ignore, line-ending, and editor configuration;
- GitHub Actions continuous integration;
- README, contribution guide, license, code of conduct, citation metadata;
- scope, reproducibility, architecture, conventions, and decision-log documents;
- placeholders for notebooks, scripts, figures, results, data, and legacy provenance;
- structural verification script and baseline test.

## Validation performed

Stage 0 should be considered complete when these commands succeed from the repository root:

```bash
python scripts/verify_repo.py
pytest
ruff check src tests scripts
ruff format --check src tests scripts
```

## Explicit deferrals

The following are intentionally deferred to Stage 1 or later:

- final physical sign conventions;
- production Hamiltonians;
- FHS/Kubo numerical routines;
- edge-state and dynamics calculations;
- manuscript figures;
- environment lock files for a submission release;
- public repository URL and DOI registration.
