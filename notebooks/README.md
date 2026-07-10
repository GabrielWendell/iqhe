# Notebooks

Notebooks are pedagogical front ends for tested source modules.  They must not contain the only
implementation of a publication result or silently change the frozen convention sheet.

## Current notebook sequence

1. `00_conventions_and_hamiltonian_core.ipynb` — Stage-1 public API and Hamiltonian checks.
2. `01_topology_reliability.ipynb` — Stage-2 Dirac warm-up, FHS/Kubo validation, direct gaps, and
   mesh convergence for the `phi=1/3` Harper-Hofstadter model.
3. `02_edge_physics.ipynb` — Stage-3 ribbon spectrum, edge participation, gap Chern numbers, and
   side-resolved oriented crossings.
4. `03_hofstadter_bulk.ipynb` — magnetic subbands, gaps, and annotated Chern numbers.
5. `04_ribbon_edge_states.ipynb` — expanded edge-state visual analysis.
6. `05_chiral_dynamics.ipynb` — Stage-6 edge-projected wave-packet dynamics.
7. `06_velocity_and_defect.ipynb` — Stage-6 velocity comparison and weak-link defect validation.

Run a notebook only after installing the editable package with:

```bash
python -m pip install -e ".[dev,notebooks]"
```
