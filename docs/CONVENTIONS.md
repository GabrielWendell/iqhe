# Physical and numerical conventions

> **Stage 1 gate:** Do not use production numerical results until every item below is completed, reviewed, and reflected in code tests.

## To be frozen in Stage 1

| Item | Chosen convention | Consequence for code and figures | Status |
|---|---|---|---|
| Electron charge sign | TBD | Peierls phase and Hall-conductivity sign | Pending |
| Magnetic-field direction | TBD | Orientation of flux and chirality | Pending |
| Gauge choice | TBD | Harper-Hofstadter hopping phases | Pending |
| Flux definition | \(\phi = \Phi/\Phi_0 = p/q\) | Magnetic unit cell and magnetic Brillouin zone | Draft |
| Flux quantum | \(\Phi_0=h/e\) | Flux normalization | Draft |
| Berry connection | TBD | Geometric-phase normalization | Pending |
| Berry curvature orientation | TBD | Kubo and FHS sign comparison | Pending |
| Chern-number convention | TBD | Reported band Chern sequence | Pending |
| Hall-conductivity convention | TBD | TKNN relation | Pending |
| Units | TBD | Group velocity and time propagation | Pending |
| Site-index convention | TBD | Matrix/vector reshaping and observables | Pending |

## Mandatory notation

- \(\mathbf{k}=(k_x,k_y)\): crystal or magnetic crystal momentum.
- \(\boldsymbol{\lambda}\): general parameter vector.
- \(|u_n(\mathbf{k})\rangle\): periodic Bloch eigenstate.
- \(E_n(\mathbf{k})\): band energy.
- \(A_{n,\mu}\): Berry connection component.
- \(\Omega_n\): Berry-curvature density.
- \(C_n\): band Chern number.
- \(\phi\): magnetic flux per plaquette in flux-quantum units.

## Stage-1 acceptance checklist

- [ ] The parent Peierls Hamiltonian is written explicitly.
- [ ] The Bloch, cylindrical, and open-boundary Hamiltonians derive from the same parent convention.
- [ ] Hermiticity is tested for all implementations.
- [ ] The FHS and Kubo formulas use compatible curvature orientation.
- [ ] The expected \(\phi=1/3\) Chern sequence is documented with its sign convention.
