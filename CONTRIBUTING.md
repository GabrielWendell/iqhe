# Contributing to QHE-EJP

## Scope

This repository supports a reproducible computational teaching article. Contributions should improve one or more of:

- scientific correctness;
- numerical validation;
- reproducibility;
- pedagogical clarity;
- maintainability.

## Ground rules

1. Do not modify `legacy/` material except to add provenance notes.
2. Do not manually edit exported figures. Change source code, regenerate the figure, and record the command.
3. Do not merge a numerical claim without a corresponding test, convergence study, or explicitly documented limitation.
4. Record changes to physical conventions or model definitions in `docs/DECISION_LOG.md`.
5. Keep notebooks focused on exposition and orchestration. Put reusable implementation in `src/qhe_ejp/`.

## Suggested branch names

```text
stage1/conventions-hamiltonian
stage2/fhs-kubo-validation
stage3/edge-participation
stage4/chiral-dynamics
fix/hermiticity-check
fig/ribbon-spectrum
```

## Local checks before a pull request

```bash
python scripts/verify_repo.py
pytest
ruff check src tests scripts
ruff format --check src tests scripts
```

## Commit-message style

Use concise imperative messages with a scope:

```text
stage1: add canonical Harper-Hofstadter Hamiltonian
fix(fhs): normalize plaquette curvature by cell area
test(dynamics): verify norm conservation
fig(ribbon): color branches by edge participation
```

## Review checklist

A proposed change should answer:

- Which convention or model definition does it use?
- Which observable or figure changes?
- How is correctness checked?
- Does it preserve reproducibility from a clean environment?
- Does the documentation need an update?
