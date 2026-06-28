# Reproducibility policy

## Principle

The computational material is part of the educational contribution. A reader should be able to reproduce every central numerical result from a clean installation of the archived repository.

## Source-of-truth hierarchy

1. `src/qhe_ejp/` — reusable scientific implementation.
2. `scripts/` — deterministic figure and validation workflows.
3. `tests/` — correctness, regression, and structural checks.
4. `notebooks/` — explanation, teaching, and reproducible walkthroughs.
5. `figures/` and `results/` — generated artifacts, never manually edited.
6. `legacy/` — frozen historical material; never the source of a publication claim.

## Environment policy

- `pyproject.toml` defines the installable package and dependency ranges.
- `environment.yml` provides a reproducible Conda/Mamba environment.
- CI validates supported Python versions independently of the developer machine.
- Before a release, record the exact resolved environment using a lock file or a platform-specific export.

## Data and artifact policy

- The project currently generates synthetic/model-based data only.
- Raw external inputs, if added, must remain immutable and be documented in `data/README.md`.
- Do not commit large binary outputs unless they are necessary reference artifacts.
- Record scripts, parameters, git commit, and package environment for all manuscript figures.

## Numerical evidence policy

Every central claim must have at least one of:

- an analytical check;
- an independent numerical implementation;
- a mesh- or system-size convergence study;
- a regression test against a documented reference value;
- a clearly stated limitation.

## Figure policy

- Do not add titles inside publication graphics.
- Use source scripts instead of manual edits.
- Save vector output for line plots where possible.
- Use shared colour scales when comparing time-evolution panels.
- Captions, rather than plot titles, carry full contextual interpretation.
