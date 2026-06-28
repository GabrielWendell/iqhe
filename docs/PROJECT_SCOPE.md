# Project scope

## Working identity

**Working title:** *From Berry Curvature to Chiral Edge Transport: A Reproducible Computational Introduction to the Integer Quantum Hall Effect*

**Target venue:** European Journal of Physics

**Primary audience:** advanced undergraduate and beginning graduate students with introductory quantum mechanics, linear algebra, matrix diagonalization, Bloch theory, and basic scientific Python.

## Central claim

The project provides a reproducible computational sequence that connects gauge-invariant Chern-number calculations to directly observable chiral edge-wave-packet propagation in the Harper-Hofstadter model.

## In scope

- massive Dirac-model warm-up for local Berry curvature;
- Fukui-Hatsugai-Suzuki discrete Berry flux and Chern numbers;
- interband Kubo curvature as an independent numerical cross-check;
- Harper-Hofstadter bulk bands at rational magnetic flux;
- ribbon spectra and quantitative edge localization;
- edge-projected wave packets, currents, leakage, centroid/arc-length motion;
- group-velocity and defect-routing validation;
- publication-quality reproducibility and educational material.

## Explicit non-goals

- a general review of every aspect of the quantum Hall effect;
- a calibrated quantitative model of a specific experimental photonic, cold-atom, or electronic platform;
- a claim of unconditional protection against arbitrary disorder;
- production use of the unvalidated legacy notebook;
- introduction of additional models unless they serve a documented pedagogical role.

## Stage map

| Stage | Objective | Exit condition |
|---|---|---|
| 0 | Repository, governance, packaging, quality, and reproducibility foundation | Clean clone passes structural checks and imports package. |
| 1 | Freeze conventions and rebuild canonical Hamiltonians | Every Hamiltonian passes Hermiticity tests. |
| 2 | Validate bulk topology | FHS and Kubo methods agree within documented mesh convergence. |
| 3 | Validate edge physics | Ribbon branches are quantified by edge participation and linked to gap Chern numbers. |
| 4 | Validate chiral dynamics | Norm, edge retention, currents, and velocity agreement are quantified. |
| 5 | Add controlled defect test and rebuild figures | Manuscript figures are reproducible from scripts. |
| 6 | Archive release and manuscript-support package | Clean installation reproduces all central results. |
