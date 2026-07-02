# Scripts

Scripts in this directory provide deterministic entry points for tasks that must be reproducible
outside notebook state.

```text
verify_repo.py            Structural and release-metadata checks
run_stage1_checks.py      Hamiltonian-core acceptance checks
run_stage2_checks.py      FHS/Kubo/gap/convergence acceptance checks
run_stage3_checks.py      Ribbon edge-localization and bulk-boundary acceptance checks
make_stage3_figures.py    Reproducible Stage-3 spectrum/profile figure generation
```

Scripts should expose arguments through `argparse` when user-configurable execution becomes necessary,
write outputs to `results/` or `figures/generated/`, and avoid interactive prompts.
