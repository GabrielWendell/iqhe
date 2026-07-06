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
\text{Berry curvature}
\longrightarrow
\text{Chern number}
\longrightarrow
\text{bulk-boundary correspondence}
\longrightarrow
\text{chiral edge-wave-packet dynamics}.
$$

The Harper-Hofstadter lattice is the central model.  The massive Dirac model is retained as a
compact warm-up for Berry curvature and lattice regularization.

## Stage 3 status

**Current stage:** Stage 3 — measurable edge physics.

Stages 1–2 freeze the Hamiltonian core and validate periodic bulk topology.  Stage 3 adds:

- explicit left/right edge-strip masks for ribbons and open finite lattices;
- quantitative edge participation, edge polarization, and inverse participation ratio diagnostics;
- x-open/y-periodic ribbon spectra on a reproducible closed-open momentum grid;
- global bulk-gap extraction and cumulative gap Chern numbers;
- edge-localized reference-energy crossing detection with measured branch orientation;
- side-resolved finite-ribbon bulk-boundary regression tests and figure builders.

Stage 2 also provides:

- a reusable periodic magnetic-Brillouin-zone mesh and one diagonalization per momentum node;
- gauge-invariant Fukui-Hatsugai-Suzuki (FHS) plaquette fluxes and Chern numbers;
- independent isolated-band interband-Kubo curvature and Chern integration;
- direct-gap diagnostics before any isolated-band topological interpretation;
- compatible FHS/Kubo density residual maps and mesh-refinement norms;
- a massive-Dirac analytic-versus-Kubo local-curvature warm-up;
- regression tests for gauge invariance, Chern values, Kubo convergence, and curvature residuals;
- a Stage-2 notebook and command-line acceptance workflow.

For the central `phi=1/3` Harper-Hofstadter model, the frozen convention target is

$$
(C_1,C_2,C_3)=(-1,2,-1),\qquad \sum_n C_n=0.
$$

Stage 3 validates the static finite-ribbon signature of bulk-boundary correspondence.  Real-space chiral
wave-packet dynamics, currents, leakage, group-velocity agreement, and defect routing remain intentionally
deferred to later stages.

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
python scripts/run_stage2_checks.py
python scripts/run_stage3_checks.py
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
python scripts/run_stage2_checks.py
python scripts/run_stage3_checks.py
pytest
```

## Minimal Stage-3 usage

```python
from qhe.models import HarperHofstadterParameters
from qhe.boundary import analyze_bulk_boundary_correspondence

params = HarperHofstadterParameters(p=1, q=3, tx=1.0, ty=1.0)
analysis = analyze_bulk_boundary_correspondence(params, bulk_nkx=41, ribbon_lx=48)
print(analysis.topology.fhs.chern_numbers)
print([summary.gap.gap_chern_number for summary in analysis.crossing_summaries])
```

## Minimal Stage-4 figure build

```bash
python scripts/make_main_figures.py
# Optional fast smoke render to a temporary output directory:
python scripts/make_main_figures.py --fast --output-dir /tmp/qhe-figures
```

The renderer exports Figures 1–6 as PDF and PNG files, plus `manifest.json`, under
`figures/generated/main/`. Figure captions are source-controlled in `figures/captions.md`.


## Development commands

```bash
python scripts/verify_repo.py
python scripts/run_stage1_checks.py
python scripts/run_stage2_checks.py
python scripts/run_stage3_checks.py
python scripts/make_main_figures.py
python scripts/run_stage4_checks.py
pytest
ruff check src tests scripts
ruff format --check src tests scripts
```

## Development commands

```bash
python scripts/verify_repo.py
python scripts/run_stage1_checks.py
python scripts/run_stage2_checks.py
python scripts/run_stage3_checks.py
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
2. `01_topology_reliability.ipynb` — Stage-2 FHS, interband Kubo, gaps, and mesh convergence.
3. `02_edge_physics.ipynb` — Stage-3 edge strips, ribbon spectra, and bulk-boundary crossings.
4. `03_hofstadter_bulk.ipynb` — planned magnetic unit-cell, bulk-band, and Chern-label exploration.
5. `04_ribbon_edge_states.ipynb` — planned expanded edge-state visual analysis.
6. `05_chiral_dynamics.ipynb` — planned projected wave packets, currents, leakage, and centroid observables.
7. `06_velocity_and_defect.ipynb` — planned group-velocity agreement and controlled defect routing.

## Citation

Please use [`CITATION.cff`](CITATION.cff).  Update the repository URL, release DOI, and author
list before making the first public release.

## License

This repository is released under the MIT License. See [`LICENSE`](LICENSE).
