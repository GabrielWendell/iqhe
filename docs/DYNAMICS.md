# Stage-6 dynamics workflow

Stage 6 adds the time-domain layer required by the EJP manuscript claim: an edge-projected
Gaussian packet is prepared in a selected bulk gap, propagated without artificial renormalization,
and compared with the corresponding ribbon edge-branch group velocity.

The validated reference case is the frozen Harper-Hofstadter model at $\phi=1/3$, with the
left edge of the first bulk gap selected by the Stage-3 ribbon crossing analysis.

## Computational sequence

1. Use the Stage-3 bulk-boundary workflow to identify a side-resolved ribbon crossing in a global
   bulk gap.
2. Build a Gaussian seed localized near the corresponding boundary and carrying the crossing
   momentum $k_y^{(0)}$.
3. Diagonalize the fully open finite Hamiltonian.
4. Select open-system eigenstates lying in the chosen bulk gap with sufficient probability on the
   selected side.
5. Project the Gaussian seed into this edge subspace using the true Hilbert-space projection
   $c_n=\langle \phi_n|g\rangle$, preserving phase information.
6. Evolve the projected state spectrally as
   $$
   |\psi(t)\rangle = \sum_n e^{-iE_nt/\hbar}|\phi_n\rangle\langle\phi_n|\psi(0)\rangle .
   $$
   The code does not renormalize the state after each time step.
7. Measure norm conservation, edge retention, bulk leakage, side-adapted centroid/arc-length motion,
   local bond currents, and packet velocity.
8. Repeat the calculation with one weakened boundary link to obtain a constrained defect-routing
   demonstration.

## Main observables

The edge and bulk probabilities are

$$
P_{\rm edge}(t)=\sum_{i\in {\rm perimeter}} |\psi_i(t)|^2,
\qquad
P_{\rm bulk}(t)=1-P_{\rm edge}(t).
$$

For the left/right edges, the side-adapted packet coordinate is the masked centroid along $y$,
which is fitted over the validation window to estimate $v_{\rm packet}$.  This is compared with

$$
v_g(k_y)=\frac{1}{\hbar}\frac{\partial E_{\rm edge}}{\partial k_y},
$$

using the branch slope already measured in the Stage-3 ribbon analysis.

The local bond-current diagnostic follows the manuscript convention

$$
J_{i\to j}(t)=\frac{2}{\hbar}\operatorname{Im}\!
\left[t_{ij}e^{i\theta_{ij}}\psi_i^*(t)\psi_j(t)\right].
$$

This provides a directional observable, so chirality is not inferred from snapshots alone.

## Validation command

```bash
python scripts/run_stage6_checks.py
```

The default validation checks that

- the clean and defect Hamiltonians remain Hermitian;
- the projected initial state is normalized;
- time evolution conserves norm to the configured tolerance;
- edge retention remains high in both clean and defect runs;
- the packet velocity agrees with the selected ribbon group velocity within the finite-size tolerance;
- the initial edge-current sign agrees with the branch orientation.

## Figure command

```bash
python scripts/make_stage6_figures.py --output-dir figures/generated/main
```

This renders Figures 7 and 8 in PDF and PNG form and writes `stage6_manifest.json`.
