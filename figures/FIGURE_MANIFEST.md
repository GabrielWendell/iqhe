# Manuscript Figure Manifest

This manifest is the source-controlled figure contract for the EJP manuscript. Every figure listed
as **implemented** is rendered only through a source script; manual edits after export are prohibited.
Figures 1--6 are rendered through `scripts/make_main_figures.py`, while the Stage-6 dynamics
figures are rendered through `scripts/make_stage6_figures.py`. The caption text lives in
[`captions.md`](captions.md).

| ID | Output stem | Status | Source builder | Main message |
| --- | --- | --- | --- | --- |
| Fig. 1 | `figure_01_conceptual_roadmap` | Implemented | `qhe.viz.plot_conceptual_roadmap` | Computational bridge from Berry curvature to boundary transport. |
| Fig. 2 | `figure_02_fhs_plaquette` | Implemented | `qhe.viz.plot_fhs_plaquette` | Gauge-invariant oriented FHS plaquette flux. |
| Fig. 3 | `figure_03_massive_dirac_warmup` | Implemented | `qhe.viz.plot_massive_dirac_warmup` | Local curvature and why a compact lattice Brillouin zone is needed for Chern numbers. |
| Fig. 4 | `figure_04_hofstadter_bulk_bands` | Implemented | `qhe.viz.plot_hofstadter_bulk_bands` | Magnetic subbands and their Chern labels at \(\phi=1/3\). |
| Fig. 5 | `figure_05_fhs_kubo_validation` | Implemented | `qhe.viz.plot_fhs_kubo_validation` | Compatible FHS/Kubo curvature validation and mesh convergence. |
| Fig. 6 | `figure_06_ribbon_bulk_boundary` | Implemented | `qhe.viz.plot_ribbon_bulk_boundary_figure` | Edge participation, reference-energy crossings, and bulk-boundary correspondence. |
| Fig. 7 | `figure_07_chiral_dynamics` | Implemented | `qhe.viz.plot_chiral_dynamics_figure` | Edge-projected packet dynamics, edge retention, centroid motion, and current direction. |
| Fig. 8 | `figure_08_velocity_and_defect` | Implemented | `qhe.viz.plot_velocity_defect_figure` | Packet/group velocity comparison and controlled weak-link defect routing. |

## Rendering contract

```bash
python scripts/make_main_figures.py
python scripts/make_stage6_figures.py --output-dir figures/generated/main
python scripts/run_stage4_checks.py
python scripts/run_stage6_checks.py
```

The static-figure command creates vector PDF and high-resolution PNG outputs for Figures 1--6 under
`figures/generated/main/`, together with `manifest.json`. The Stage-6 command creates the dynamics
figures and a `stage6_manifest.json` file in the same output directory. The acceptance scripts render
fresh temporary copies and check the file contract, source-to-caption mapping, no-title policy, and
time-domain validation thresholds.
