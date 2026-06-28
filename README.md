# QHE-EJP

> **A reproducible computational teaching project on the integer quantum Hall effect.**

`qhe-ejp` is the code, notebook, validation, and figure-generation repository supporting the planned European Journal of Physics (EJP) article:

> *From Berry Curvature to Chiral Edge Transport: A Reproducible Computational Introduction to the Integer Quantum Hall Effect*

The project is designed for advanced undergraduates and beginning graduate students who know introductory quantum mechanics, linear algebra, matrix diagonalization, Bloch theory, and basic scientific Python.

## Scientific and pedagogical objective

The repository implements one coherent computational route:

$$
\text{Berry curvature}
\longrightarrow
\text{Chern number}
\longrightarrow
\text{bulk-boundary correspondence}
\longrightarrow
\text{chiral edge-wave-packet dynamics}.
$$

The production workflow will use a Harper-Hofstadter lattice as the central model. The massive Dirac model is retained as a compact warm-up for Berry curvature and lattice regularization.

## Stage 0 status

Stage 0 establishes the project foundation. It provides:

- a `src/`-layout Python package;
- Conda and pip installation routes;
- test, lint, and formatting configuration;
- GitHub Actions continuous integration;
- reproducibility, data, governance, and decision-log templates;
- a directory structure for notebooks, figures, results, documentation, and legacy material.

No scientific production results are claimed at this stage. Stage 1 will freeze physical conventions and rebuild the canonical Harper-Hofstadter Hamiltonian from a single verified Peierls-substituted definition.

## Repository layout

```text
qhe-ejp/
├── src/qhe_ejp/          # Reusable implementation modules
├── tests/                # Unit and regression tests
├── notebooks/            # Pedagogically ordered notebooks
├── scripts/              # Reproducible command-line workflows
├── configs/              # Runtime/model configuration files
├── docs/                 # Scope, conventions, decisions, reproducibility
├── figures/              # Generated figures only; never edited manually
├── results/              # Reproducible numerical outputs and summaries
├── data/                 # Small tracked inputs; large assets excluded by policy
├── legacy/               # Frozen prototype notebook and historical material
└── .github/workflows/    # Continuous integration
```

## Quick start

### Option A — Conda / Mamba

```bash
conda env create -f environment.yml
conda activate qhe-ejp
python scripts/verify_repo.py
pytest
```

### Option B — virtual environment + pip

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/verify_repo.py
pytest
```

## Development commands

```bash
python scripts/verify_repo.py      # Stage-0 structural checks
pytest                             # Unit tests
ruff check src tests scripts        # Lint
ruff format --check src tests scripts
```

## Reproducibility rules

1. Raw or externally supplied material is never modified in place.
2. Every manuscript figure must be generated from version-controlled code.
3. Numerical claims must have a corresponding validation test or documented convergence study.
4. Notebook cells explain and orchestrate calculations; reusable physics belongs in `src/qhe_ejp/`.
5. The legacy notebook is preserved for provenance but is not the production source of truth.
6. All physical sign and gauge conventions must be recorded in `docs/CONVENTIONS.md` before Stage 1 results are used in the manuscript.

See [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) and [docs/DECISION_LOG.md](docs/DECISION_LOG.md) for the operational policy.

## Planned notebook sequence

1. `00_project_setup.ipynb` — conventions, units, dependencies, and verification.
2. `01_dirac_curvature.ipynb` — Berry curvature in the massive Dirac warm-up.
3. `02_fhs_kubo_validation.ipynb` — discrete FHS flux versus interband Kubo curvature.
4. `03_hofstadter_bulk.ipynb` — magnetic unit cell, bulk bands, gaps, and Chern numbers.
5. `04_ribbon_edge_states.ipynb` — edge participation and bulk-boundary correspondence.
6. `05_chiral_dynamics.ipynb` — projected packets, currents, leakage, and centroid observables.
7. `06_velocity_and_defect.ipynb` — group-velocity agreement and controlled defect routing.

The notebooks above are placeholders in Stage 0 and will be implemented incrementally.

## Citation

Please use the citation metadata in [`CITATION.cff`](CITATION.cff). Update the repository URL, release DOI, and author list before making the first public release.

## License

This repository is released under the MIT License. See [`LICENSE`](LICENSE).

## Project status

**Current stage:** Stage 0 — repository foundation.

**Next stage:** Stage 1 — conventions, canonical Hamiltonians, and core validation tests.
