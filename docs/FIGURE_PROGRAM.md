# Figure Programme and Teaching-Notebook Policy

## Purpose

Stage 4 transforms the validated Stage-1–3 calculations into an auditable manuscript figure
programme. It ensures that every *currently supported* main figure is produced from source code,
has a self-contained manuscript caption, uses a shared project visual language, and can be rebuilt
from a clean installed environment.

Stage 4 does **not** fabricate time-domain figures before the packet-dynamics machinery exists.
Figures 7–8 are registered as reserved and become mandatory only after Stages 5–6 implement
edge-projected dynamics, common colour-scale heat maps, current diagnostics, velocity validation,
and a controlled defect calculation.

## Single source of truth

- Figure IDs, source builders, status, and output stems: `figures/FIGURE_MANIFEST.md`.
- Caption text: `figures/captions.md`.
- Frozen numerical parameters: `configs/figure_program_phi_1_3.toml`.
- Renderer: `scripts/make_main_figures.py`.
- Acceptance script: `scripts/run_stage4_checks.py`.
- Reusable builders: `src/qhe/viz/`.

## Implemented figures

The current figure programme renders Figures 1–6. Each plot is title-free; captions and `(a)`,
`(b)`, … panel labels provide the narrative. Curvature comparisons use compatible FHS flux-density
and plaquette-averaged Kubo density. The same style module controls font sizes, ticks, vector text,
colour semantics, and export formats.

## Teaching notebooks

The notebooks are deliberately shorter than the corresponding source scripts. They explain the
calculation and link to tested APIs, but they do not contain an independent physics implementation.
The Stage-4 sequence is:

1. `00_conventions_and_hamiltonian_core.ipynb` — frozen signs, gauge, and Hamiltonians.
2. `01_topology_reliability.ipynb` — FHS/Kubo comparison and Chern convergence.
3. `02_edge_physics.ipynb` — edge participation and oriented ribbon crossings.
4. `03_hofstadter_bulk.ipynb` — figure-oriented bulk subbands and Chern labels.
5. `04_ribbon_edge_states.ipynb` — figure-oriented static bulk-boundary correspondence.
6. `05_chiral_dynamics.ipynb` — reserved for Stage 5.
7. `06_velocity_and_defect.ipynb` — reserved for Stage 5/6.

## Rendering commands

```bash
python scripts/make_main_figures.py
python scripts/run_stage4_checks.py
```

The first command writes PDF, PNG, and a machine-readable manifest under
`figures/generated/main/`. The second command performs an isolated smoke render into a temporary
directory, validates every generated file, checks caption/figure coverage, and records the command
contract. The default renderer never mutates notebooks and never requests interactive input.

## Exit gate

Stage 4 is complete when:

- every implemented figure has a version-controlled builder, source configuration, self-contained
  caption, PDF output, PNG output, and manifest record;
- no generated axis has an in-plot title;
- FHS/Kubo comparison panels use compatible numerical objects and shared colour normalization;
- figures are regenerated from a clean package installation through one command;
- the teaching notebooks delegate all numerical work to the tested package API.
