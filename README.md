# QHE-EJP

> **A reproducible computational teaching project on the integer quantum Hall effect.**

QHE-EJP is the source-code, notebook, validation, and figure-generation repository supporting the
planned European Journal of Physics article:

> *From Berry Curvature to Chiral Edge Transport: A Reproducible Computational Introduction to the
> Integer Quantum Hall Effect*

The project is designed for advanced undergraduates and beginning graduate students with introductory
quantum mechanics, linear algebra, matrix diagonalization, Bloch theory, and basic scientific Python.

## Scientific and pedagogical objective

The repository implements one computational chain:

$$
\text{Berry curvature}
\longrightarrow
\text{Chern number}
\longrightarrow
\text{bulk-boundary correspondence}
\longrightarrow
\text{chiral edge-wave-packet dynamics}.
$$

The Harper-Hofstadter lattice is the central model. The massive Dirac model is retained as a compact
warm-up for Berry curvature and the role of lattice regularization.

## Release status

**Current release:** `v0.7.0` — chiral-dynamics validation baseline.

The release verifies the Hamiltonian core, bulk topology, FHS/interband-Kubo agreement, ribbon edge
localization, measurable static bulk-boundary correspondence, time-domain edge-projected propagation,
norm conservation, edge retention, bond-current directionality, packet/group-velocity agreement, and one
controlled weak-link defect-routing demonstration. It regenerates manuscript Figures 1–8 from source
scripts and executes the Stage 1–6 teaching notebooks.

For the central $\phi=1/3$ Harper-Hofstadter model, the frozen convention target is

$$
(C_1,C_2,C_3)=(-1,2,-1),\qquad \sum_n C_n=0.
$$

## Quick reproducible install

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

The release smoke test runs the structural checks, Stage 1–4 and Stage-6 validations, tests, all
production teaching notebooks, and clean regeneration of Figures 1–8. Details are in
[`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md).

## Main commands

```bash
# Structural and scientific validation
python scripts/verify_repo.py
python scripts/run_stage1_checks.py
python scripts/run_stage2_checks.py
python scripts/run_stage3_checks.py
python scripts/run_stage4_checks.py
python scripts/run_stage6_checks.py
pytest

# Execute all production teaching notebooks non-interactively
python scripts/execute_notebooks.py

# Rebuild the current manuscript figures (PDF + PNG + manifest)
python scripts/make_main_figures.py
python scripts/make_stage6_figures.py --output-dir figures/generated/main

# Verify release metadata and create local release assets
python scripts/check_release_metadata.py --tag v0.7.0
python scripts/create_release_archive.py --tag v0.7.0
```

Equivalent Make targets are available through `make verify`, `make stage-checks`, `make notebooks`,
`make figures`, `make smoke`, `make build`, and `make archive`.

## Repository layout

```text
qhe-ejp/
├── src/qhe/              # Reusable physics, topology, boundary, and visualization modules
├── tests/                # Unit and numerical-regression tests
├── notebooks/            # Pedagogically ordered executable notebooks
├── scripts/              # Deterministic validation, notebook, figure, and release workflows
├── configs/              # Version-controlled model and figure parameters
├── docs/                 # Conventions, architecture, reproducibility, release, and data policies
├── figures/              # Caption/manifest sources and generated figure outputs
├── results/              # Reproducible summaries and generated local artifacts
├── requirements/         # Tested environment snapshots
├── release/              # Release notes and release checklist
├── legacy/               # Frozen historical notebook and provenance records
└── .github/workflows/    # Fresh-install CI and tag-triggered release automation
```

## Notebook sequence

1. `00_conventions_and_hamiltonian_core.ipynb` — canonical Hamiltonians and Stage 1 checks.
2. `01_topology_reliability.ipynb` — FHS, interband Kubo, gaps, and mesh convergence.
3. `02_edge_physics.ipynb` — edge masks, ribbon spectra, and bulk-boundary crossings.
4. `03_hofstadter_bulk.ipynb` — magnetic unit cell, bulk bands, and Chern labels.
5. `04_ribbon_edge_states.ipynb` — expanded ribbon and edge-state analysis.
6. `05_chiral_dynamics.ipynb` — edge-projected wave-packet dynamics.
7. `06_velocity_and_defect.ipynb` — packet/group-velocity comparison and weak-link defect validation.

## Data availability

No external empirical data are used in the current release. All outputs are deterministic model
calculations generated from the source code and configurations. See
[`docs/DATA_AVAILABILITY.md`](docs/DATA_AVAILABILITY.md) for the manuscript-ready statement and
archival-DOI policy.

## Citation

Use [`CITATION.cff`](CITATION.cff) to cite the repository. The release tag should be archived with a DOI
before manuscript submission; do not add a DOI to the citation metadata until it has been issued.

## License

This project is released under the [MIT License](LICENSE).
