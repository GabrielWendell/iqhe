# Methodological decision log

Use this log for decisions that affect physical conventions, numerical reproducibility, interpretation, or manuscript claims.

| ID | Date | Decision | Rationale | Consequences | Owner | Status |
|---|---|---|---|---|---|---|
| D-000 | 2026-06-28 | Establish Stage 0 repository foundation before revising production code. | The legacy notebook mixes prototype logic, narrative, plotting, and unvalidated claims. | Stage 1 will rebuild a canonical, tested core rather than patching individual cells. | Project team | Accepted |
| D-001 | TBD | Freeze Berry-curvature, Chern-number, charge, gauge, and Hall-conductivity sign conventions. | Required before numerical and manuscript claims can be compared consistently. | Populate `docs/CONVENTIONS.md`; update all modules, figures, and tests. | TBD | Pending |

## Entry template

```text
| D-XXX | YYYY-MM-DD | <decision> | <why this was chosen> | <what changes downstream> | <owner> | Proposed / Accepted / Superseded |
```
