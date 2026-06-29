# QHE-EJP

> **A reproducible computational teaching project on the integer quantum Hall effect.**

`qhe-ejp` is the code, notebook, validation, and figure-generation repository supporting the
planned European Journal of Physics (EJP) article:

> *From Berry Curvature to Chiral Edge Transport: A Reproducible Computational Introduction to
> the Integer Quantum Hall Effect*

The project is designed for advanced undergraduates and beginning graduate students who know
introductory quantum mechanics, linear algebra, matrix diagonalization, Bloch theory, and basic
scientific Python.

## Scientific and pedagogical objective

The repository implements one coherent computational route:

$$
	ext{Berry curvature}
\longrightarrow
	ext{Chern number}
\longrightarrow
	ext{bulk-boundary correspondence}
\longrightarrow
	ext{chiral edge-wave-packet dynamics}.
$$

The Harper-Hofstadter lattice is the central model.  The massive Dirac model is retained as a
compact warm-up for Berry curvature and lattice regularization.

## Stage 1 status

**Current stage:** Stage 1 — frozen conventions and canonical Hamiltonian core.

Stage 1 replaces legacy prototype definitions with one tested Harper-Hofstadter parent model in
Landau gauge.  The repository now provides:

- a frozen convention sheet in [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md);
- canonical open, ribbon, and magnetic-Bloch Harper-Hofstadter Hamiltonians;
- a rectangular-lattice-safe site-index convention;
- analytic magnetic-Bloch derivatives for later Kubo-curvature validation;
- a massive two-band Dirac warm-up Hamiltonian;
- regression tests for Hermiticity, phases, indexing, and derivatives;
- a notebook that demonstrates the public Stage-1 API.

Stage 1 deliberately does **not** yet make a Chern-number, FHS/Kubo, edge-state, or dynamics
claim.  Those are Stage-2 and later validation tasks.

## Repository layout

```text
qhe-ejp/
├── src/qhe/              # Reusable implementation modules
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
conda activate qhe
python scripts/verify_repo.py
python scripts/run_stage1_checks.py
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
python -m pip install -e ".[dev,notebooks]"
python scripts/verify_repo.py
python scripts/run_stage1_checks.py
pytest
```

## Minimal Stage-1 usage

```python
from qhe.models import HarperHofstadterParameters, bloch_hamiltonian, open_hamiltonian

params = HarperHofstadterParameters(p=1, q=3, tx=1.0, ty=1.0)
h_bulk = bloch_hamiltonian(kx=0.0, ky=0.0, parameters=params)
h_open = open_hamiltonian(lx=24, ly=30, parameters=params)
```

## Development commands

```bash
python scripts/verify_repo.py
python scripts/run_stage1_checks.py
pytest
ruff check src tests scripts
ruff format --check src tests scripts
```

## Reproducibility rules

1. Raw or externally supplied material is never modified in place.
2. Every manuscript figure is generated from version-controlled code.
3. Numerical claims have a corresponding test or documented convergence study.
4. Notebook cells explain and orchestrate calculations; reusable physics belongs in `src/qhe/`.
5. The legacy notebook is preserved for provenance but is not the production source of truth.
6. Physical signs, gauge choices, and units are frozen in `docs/CONVENTIONS.md`.

## Planned notebook sequence

1. `00_conventions_and_hamiltonian_core.ipynb` — Stage-1 checks and canonical Hamiltonians.
2. `01_dirac_curvature.ipynb` — Berry curvature in the massive Dirac warm-up.
3. `02_fhs_kubo_validation.ipynb` — discrete FHS flux versus interband Kubo curvature.
4. `03_hofstadter_bulk.ipynb` — magnetic unit cell, bulk bands, gaps, and Chern numbers.
5. `04_ribbon_edge_states.ipynb` — edge participation and bulk-boundary correspondence.
6. `05_chiral_dynamics.ipynb` — projected packets, currents, leakage, and centroid observables.
7. `06_velocity_and_defect.ipynb` — group-velocity agreement and controlled defect routing.

## Citation

Please use [`CITATION.cff`](CITATION.cff).  Update the repository URL, release DOI, and author
list before making the first public release.

## License

This repository is released under the MIT License. See [`LICENSE`](LICENSE).
