# Stage 4 — Rebuild figures and teaching notebooks

## Objective

Stage 4 operationalizes the EJP figure programme for the validated static portion of the project.
It replaces notebook-only plotting with deterministic, source-controlled builders and a
caption/manifest contract. The implemented figures are the conceptual roadmap, FHS plaquette,
Dirac warm-up, Hofstadter magnetic subbands, FHS/Kubo validation, and measurable
bulk-boundary correspondence.

## Delivered components

- `qhe.viz.schematics` for vector conceptual and FHS figures;
- `qhe.viz.topology` for Dirac, magnetic-subband, and FHS/Kubo figures;
- `qhe.viz.manuscript` for the two-panel bulk-boundary figure;
- `scripts/make_main_figures.py` for deterministic PDF/PNG export and machine-readable metadata;
- `figures/FIGURE_MANIFEST.md` and `figures/captions.md` as the manuscript figure contract;
- `configs/figure_program_phi_1_3.toml` as the frozen figure-build configuration;
- `notebooks/03_hofstadter_bulk.ipynb` and `notebooks/04_ribbon_edge_states.ipynb` as teaching
  front ends for the static figure workflow;
- `scripts/run_stage4_checks.py` plus Stage-4 regression tests.

## Scope boundary

The programme registers, but does not generate, the planned dynamics and velocity/defect figures.
Those require the Stage-5 dynamics engine. This explicit reservation is a correctness feature: the
repository does not create pedagogical graphics for quantities it has not yet computed.

## Operational commands

```bash
python scripts/make_main_figures.py
python scripts/run_stage4_checks.py
pytest
```

## Exit criterion

A fresh editable installation can run the figure renderer and reproduce all currently implemented
main figures, including PDF/PNG files and manifest metadata, without notebook state or manual
plot editing.
