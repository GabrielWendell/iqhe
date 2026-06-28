# Software architecture

## Design principle

The codebase separates four responsibilities:

1. **physics definitions** — Hamiltonians, gauges, units, and model parameters;
2. **topological algorithms** — FHS links/plaquettes, Kubo curvature, integration, convergence;
3. **boundary and dynamics analysis** — ribbon spectra, edge metrics, projected packets, currents, observables;
4. **presentation** — notebooks, figure scripts, and publication styling.

## Package map

```text
qhe_ejp/
├── models/       # Dirac, honeycomb, Harper-Hofstadter Hamiltonians
├── topology/     # FHS, interband Kubo, Chern integration, convergence
├── boundary/     # Cylindrical/open geometries, edge masks, participation
├── dynamics/     # State preparation, propagation, currents, diagnostics
├── viz/          # Shared plotting style and figure builders
├── io/           # Result tables, metadata, serialization
└── validation/   # Higher-level scientific acceptance checks
```

## Boundary between notebooks and modules

Notebooks may:

- explain the physics;
- call public functions from `src/qhe_ejp/`;
- render pedagogical intermediate plots;
- demonstrate parameter choices.

Notebooks must not:

- contain the only implementation of a publication result;
- silently redefine physical conventions;
- manually alter figure data;
- duplicate nontrivial numerical algorithms.

## Initial public API direction

Stage 1 will introduce, at minimum:

```python
from qhe_ejp.models.harper_hofstadter import (
    bloch_hamiltonian,
    open_hamiltonian,
    ribbon_hamiltonian,
)
from qhe_ejp.validation import assert_hermitian
```

The exact API will be finalized after conventions are frozen.
