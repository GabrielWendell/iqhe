# Stage 2 — Make topology reliable

## Objective

Stage 2 establishes reproducible, independently cross-checked bulk-topology calculations for the
canonical Harper-Hofstadter Hamiltonian frozen in Stage 1.  It implements the two numerical routes
that support the EJP article's central bulk claim:

1. gauge-invariant discrete Berry flux via the Fukui-Hatsugai-Suzuki (FHS) construction;
2. pointwise Berry-curvature density via the isolated-band interband Kubo formula.

The massive Dirac model remains a local warm-up: its analytic curvature is compared with the Kubo
implementation at selected momentum points, but it is not assigned a lattice Chern number.

## Frozen numerical objects

For the project convention

\[
A_{n,\mu}=i\langle u_n|\partial_{k_\mu}u_n\rangle,
\qquad
\Omega_n=\partial_{k_x}A_{n,y}-\partial_{k_y}A_{n,x},
\]

an FHS link carries the phase of \(\langle u_n(\mathbf{k})|u_n(\mathbf{k}+\Delta\mathbf{k})\rangle\),
which is minus the Berry-connection line element.  Therefore the implemented plaquette flux is

\[
\widetilde F_{12}(\mathbf{k})=-\operatorname{Arg}
\left[U_x(\mathbf{k})U_y(\mathbf{k}+\hat x)
U_x^{-1}(\mathbf{k}+\hat y)U_y^{-1}(\mathbf{k})\right].
\]

The matching interband Kubo expression is

\[
\Omega_n(\mathbf{k})=-2\operatorname{Im}\sum_{m\ne n}
\frac{\langle n|\partial_{k_x}H|m\rangle
\langle m|\partial_{k_y}H|n\rangle}
{[E_m(\mathbf{k})-E_n(\mathbf{k})]^2}.
\]

FHS returns an integrated plaquette flux, whereas Kubo returns a density.  The Stage-2 comparison
therefore uses \(\widetilde F_{12}/(\Delta k_x\Delta k_y)\) against the average Kubo density over
the four vertices of the same periodic plaquette.

## Implemented modules

- `qhe.topology.mesh`
  - uniform closed-open magnetic-Brillouin-zone meshes;
  - one diagonalization per momentum node;
  - reusable `BandMesh` storage of energies and eigenvectors.
- `qhe.topology.fhs`
  - normalized U(1) overlap links;
  - oriented FHS plaquette fluxes;
  - gauge-invariant Chern numbers and link-overlap diagnostics.
- `qhe.topology.kubo`
  - isolated-band Kubo curvature at a point or on an entire mesh;
  - minimum direct gap diagnostics;
  - mesh-integrated Kubo Chern estimates.
- `qhe.topology.convergence`
  - compatible FHS/Kubo density residual maps;
  - L2 and Linf curvature errors;
  - mesh-refinement tables for the `phi=1/3` model.

## Acceptance criteria

Stage 2 is complete only when all of the following conditions hold.

- The FHS calculation returns band Chern numbers `(-1, 2, -1)` for `phi=1/3`, up to the frozen
  convention, and their sum is zero.
- The Kubo-integrated Chern numbers converge to the same sequence with mesh refinement.
- The adjacent-band direct gaps remain positive on every validation mesh.
- FHS/Kubo curvature-density residual norms decrease under refinement.
- The FHS result is invariant under arbitrary smooth or random U(1) phase choices for eigenvectors.
- The Dirac Kubo curvature agrees with the analytic massive-Dirac expression at representative
  momentum points.
- The stage checks and full unit-test suite pass from a clean editable installation.

## Operational commands

```bash
python scripts/run_stage2_checks.py
pytest
```

For the pedagogical workflow, run:

```text
notebooks/01_topology_reliability.ipynb
```

## Outputs deferred to later stages

Stage 2 validates periodic bulk topology only.  It does not yet claim edge localization,
bulk-boundary correspondence, chiral wave-packet transport, group-velocity agreement, or defect
routing.  Those claims require the Stage-3 and later boundary/dynamics implementations.
