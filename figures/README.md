# Figures

This directory contains the source-controlled manuscript figure programme.

## Stage-4 workflow

- Figure IDs, builders, status, and output stems: [`FIGURE_MANIFEST.md`](FIGURE_MANIFEST.md).
- Self-contained manuscript captions: [`captions.md`](captions.md).
- Frozen parameters: `configs/figure_program_phi_1_3.toml`.
- Deterministic renderer: `python scripts/make_main_figures.py`.
- Clean-render acceptance check: `python scripts/run_stage4_checks.py`.

Generated PDF/PNG files and `manifest.json` are written to `figures/generated/main/`. They must never
be manually edited after export. The renderer regenerates the full current figure programme from
package APIs rather than notebook state.

Figures 7–8 are deliberately registered as future outputs. They require the dynamics and velocity
validation implemented only in later stages.
