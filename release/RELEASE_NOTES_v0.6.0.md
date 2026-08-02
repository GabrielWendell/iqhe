# IQHE v0.6.0 — static-topology reproducibility release

## Summary

This release packages the reproducible computational core supporting the static portion of the planned teaching article, *From Berry Curvature to Chiral Edge Transport: A Reproducible Computational Introduction to the Integer Quantum Hall Effect*.

## Included scientific scope

- frozen sign, gauge, momentum-space, and units conventions;
- canonical Hermitian Harper-Hofstadter Hamiltonians for Bloch, ribbon, and open geometries;
- FHS and interband-Kubo Berry-curvature/Chern-number cross-validation;
- positive direct-gap diagnostics and mesh-convergence checks;
- measurable finite-ribbon bulk-boundary correspondence through edge participation and oriented crossings;
- deterministic source generation for manuscript Figures 1–6;
- executable teaching notebooks for the validated Stage 1–4 workflow.

For the central $\phi=1/3$ model, the release reproduces the frozen Chern sequence $(C_1,C_2,C_3)=(-1,2,-1)$, subject to the documented convention.

## Reproduce locally

```bash
python -m pip install -e ".[dev,notebooks,release]"
python scripts/run_release_smoke.py
```

## Not included

This release intentionally does **not** claim a validated time-domain chiral-dynamics calculation. The
following remain future work: edge-projected Gaussian packet propagation, norm-conservation records,
edge leakage, bond-current maps, packet/group-velocity comparison, and controlled defect routing.

## Citation and archival record

Use `CITATION.cff` to cite the software. A DOI archive should be created after publication of the GitHub
tagged release and added to the software metadata before manuscript submission.
