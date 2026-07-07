# Stage 5 — Release package

## Objective

Stage 5 converts the validated Stage 1–4 project into a release-ready reproducibility package. The goal is
that a fresh checkout can install its dependencies, run validation, execute teaching notebooks, regenerate
the implemented figures, and build distributable artifacts without manual intervention.

## Delivered components

- synchronized package, citation, changelog, and release-note version metadata for `0.6.0`;
- a clear public README, environment guide, data-availability statement, and release procedure;
- an exact Stage 5 environment snapshot plus an exporter for future platform snapshots;
- deterministic notebook execution via `scripts/execute_notebooks.py`;
- full release smoke testing via `scripts/run_release_smoke.py`;
- release metadata verification via `scripts/check_release_metadata.py`;
- source-archive production via `scripts/create_release_archive.py`;
- annotated tag creation via `scripts/create_release_tag.py`;
- continuous-integration and tag-triggered GitHub Release workflows;
- source-distribution inclusion rules in `MANIFEST.in`;
- release-oriented regression tests.

## Exit criterion

A fresh checkout running:

```bash
python -m pip install -e ".[dev,notebooks,release]"
python scripts/run_release_smoke.py
```

must run the structural checks, Stage 1–4 validations, test suite, production notebooks, and a clean
Figure 1–6 regeneration. The CI workflow enforces the same sequence on supported Python versions.

## Scope boundary

This release packages the static topology and bulk-boundary workflow. It does not fabricate future
time-domain results. Chiral dynamics, current maps, velocity agreement, and defect bypass remain future
validated deliverables.
