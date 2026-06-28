# Scripts

Scripts in this directory provide deterministic entry points for tasks that must be reproducible outside notebook state.

Planned scripts:

```text
verify_repo.py              Stage-0 structural checks
run_validation_suite.py     Scientific acceptance tests
make_all_figures.py         Regenerate manuscript figures
export_run_manifest.py      Capture parameters, git revision, and environment
```

Scripts should expose arguments through `argparse`, write outputs to `results/` or `figures/generated/`, and avoid interactive prompts.
