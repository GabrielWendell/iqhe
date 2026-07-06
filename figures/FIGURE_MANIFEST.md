# Manuscript Figure Manifest

This manifest is the source-controlled figure contract for the EJP manuscript. Every figure listed
as **implemented** is rendered only through `scripts/make_main_figures.py`; manual edits after
export are prohibited. The caption text lives in [`captions.md`](captions.md).

| ID | Output stem | Status | Source builder | Main message |
| --- | --- | --- | --- | --- |
| Fig. 1 | `figure_01_conceptual_roadmap` | Implemented | `qhe.viz.plot_conceptual_roadmap` | Computational bridge from Berry curvature to boundary transport. |
| Fig. 2 | `figure_02_fhs_plaquette` | Implemented | `qhe.viz.plot_fhs_plaquette` | Gauge-invariant oriented FHS plaquette flux. |
| Fig. 3 | `figure_03_massive_dirac_warmup` | Implemented | `qhe.viz.plot_massive_dirac_warmup` | Local curvature and why a compact lattice Brillouin zone is needed for Chern numbers. |
| Fig. 4 | `figure_04_hofstadter_bulk_bands` | Implemented | `qhe.viz.plot_hofstadter_bulk_bands` | Magnetic subbands and their Chern labels at \(\phi=1/3\). |
| Fig. 5 | `figure_05_fhs_kubo_validation` | Implemented | `qhe.viz.plot_fhs_kubo_validation` | Compatible FHS/Kubo curvature validation and mesh convergence. |
| Fig. 6 | `figure_06_ribbon_bulk_boundary` | Implemented | `qhe.viz.plot_ribbon_bulk_boundary_figure` | Edge participation, reference-energy crossings, and bulk-boundary correspondence. |
| Fig. 7 | `figure_07_chiral_dynamics` | Reserved for Stage 5 | Stage-5 dynamics builders | Edge-projected packet dynamics with common colour scales. |
| Fig. 8 | `figure_08_velocity_and_defect` | Reserved for Stage 5/6 | Stage-5/6 dynamics builders | Packet/group velocity comparison and controlled defect bypass. |

## Rendering contract

```bash
python scripts/make_main_figures.py
python scripts/run_stage4_checks.py
```

The default command creates both vector PDF and high-resolution PNG outputs under
`figures/generated/main/`, together with `manifest.json`. The Stage-4 acceptance script renders a
fresh temporary copy and checks the file contract, source-to-caption mapping, and no-title policy.
