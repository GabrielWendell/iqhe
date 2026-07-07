# Changelog

All notable changes to QHE-EJP are documented in this file.

The project follows a staged scientific-reproducibility workflow. Version numbers describe
repository releases, not completion of the companion manuscript.

## [0.6.0] — 2026-07-06

### Added

- release metadata synchronized across `pyproject.toml`, `qhe.__version__`, and `CITATION.cff`;
- `docs/DATA_AVAILABILITY.md`, `docs/ENVIRONMENT.md`, `docs/RELEASE.md`, and this changelog;
- exact release-environment snapshot and documented environment refresh procedure;
- deterministic notebook executor and release smoke-test workflow;
- source-archive builder, release metadata checker, and annotated-tag helper;
- GitHub Actions CI and tag-triggered release workflow;
- release notes and a release checklist for the `v0.6.0` static-topology baseline;
- regression tests for release metadata, notebook discovery, and provenance checks.

### Changed

- README rewritten around a clean-install/reproduce/release workflow;
- Conda environment now includes notebook execution and release dependencies;
- repository URLs now point to `GabrielWendell/qhe-ejp`;
- legacy provenance references now use the actual import package name `qhe`.

### Verified scope

- canonical Harper-Hofstadter Hamiltonians and frozen sign conventions;
- FHS and interband-Kubo bulk-topology validation for \(\phi=1/3\);
- measurable static bulk-boundary correspondence in a finite ribbon;
- deterministic generation of manuscript Figures 1–6;
- executable Stage 1–4 teaching notebooks.

### Not included

- time-domain edge-projected wave-packet dynamics;
- norm-conservation, current, leakage, velocity, and defect-routing figures;
- a manuscript DOI or Zenodo archive DOI.

## [0.5.0] — Stage 4 internal milestone

- Deterministic static figure programme and teaching notebooks.

## [0.4.0] — Stage 3 internal milestone

- Quantitative ribbon-edge and bulk-boundary workflow.

## [0.3.0] — Stage 2 internal milestone

- FHS/interband-Kubo bulk-topology validation and convergence diagnostics.

## [0.2.0] — Stage 1 internal milestone

- Frozen conventions and canonical Hamiltonian core.

## [0.1.0] — Stage 0 internal milestone

- Repository scaffold, governance, packaging, and testing foundation.
