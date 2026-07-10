# Release notes — v0.7.0

This release adds Stage 6: chiral edge-wave-packet dynamics, velocity validation, and a controlled weak-link defect demonstration.

## Highlights

- proper phase-preserving projection of Gaussian edge seeds onto selected edge eigenspaces;
- unitary spectral propagation without artificial time-step renormalization;
- norm, edge-retention, bulk-leakage, centroid, velocity, current, and defect diagnostics;
- new Stage-6 figures: `figure_07_chiral_dynamics` and `figure_08_velocity_and_defect`;
- new notebooks: `05_chiral_dynamics.ipynb` and `06_velocity_and_defect.ipynb`.

## Validation

Run:

```bash
python scripts/run_stage6_checks.py
python scripts/make_stage6_figures.py --output-dir figures/generated/main
```
