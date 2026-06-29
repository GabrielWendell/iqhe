# Stage 1 — Freeze conventions and rebuild the Hamiltonian core

## Objective

Replace the legacy notebook's independent and partially inconsistent Hamiltonian definitions
with a single convention-controlled implementation.  Stage 1 does **not** claim production
Chern numbers, edge transport, or dynamics results.  Its purpose is to make all later results
traceable to one tested parent model.

## Deliverables completed

1. `docs/CONVENTIONS.md` freezes charge, gauge, units, Berry, Chern, Hall-response, Fourier,
   and site-index conventions.
2. `src/qhe/models/harper_hofstadter.py` supplies open, ribbon, magnetic-Bloch, and derivative
   implementations from a common Peierls Hamiltonian.
3. `src/qhe/models/dirac.py` supplies a compact convention-consistent massive Dirac warm-up.
4. `configs/harper_hofstadter_phi_1_3.toml` records the primary model configuration.
5. Tests cover Hermiticity, flux validation, Peierls phases, rectangular indexing, magnetic-BZ
   dimensions, and analytic-derivative agreement with finite differences.
6. `notebooks/00_conventions_and_hamiltonian_core.ipynb` demonstrates the new API without
   duplicating the implementation.

## Public Stage-1 API

```python
from qhe.models import (
    HarperHofstadterParameters,
    bloch_hamiltonian,
    bloch_hamiltonian_derivatives,
    open_hamiltonian,
    ribbon_hamiltonian,
)

params = HarperHofstadterParameters(p=1, q=3, tx=1.0, ty=1.0)
h_bulk = bloch_hamiltonian(kx=0.0, ky=0.0, parameters=params)
h_ribbon = ribbon_hamiltonian(lx=48, ky=0.2, parameters=params)
h_open = open_hamiltonian(lx=24, ly=30, parameters=params)
```

## Acceptance commands

```bash
python scripts/verify_repo.py
python scripts/run_stage1_checks.py
pytest
ruff check src tests scripts
ruff format --check src tests scripts
```

## Explicit non-goals

- No FHS Chern-number implementation yet.
- No Kubo/interband curvature implementation yet.
- No edge-state classifier, wave-packet projection, propagation, currents, or figures yet.
- No manuscript-ready numerical claim yet.

These are intentional Stage-2 and later deliverables.
