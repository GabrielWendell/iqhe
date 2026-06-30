# Topology implementation notes

## Why the mesh stores eigenvectors once

The legacy notebook repeatedly diagonalized a Bloch Hamiltonian inside multiple plotting and
plaquette loops.  Stage 2 samples the Hamiltonian once on a periodic mesh and stores:

```text
energies[N_kx, N_ky, N_band]
eigenvectors[N_kx, N_ky, N_orbital, N_band]
```

Both FHS and Kubo calculations consume this same `BandMesh`.  This removes a potential source of
hidden mismatches between algorithms and makes all convergence plots traceable to one grid.

## FHS comparison rule

`FHSResult.plaquette_flux` is dimensionless.  `KuboResult.curvature_density` has dimensions of
momentum-space area inverse.  Directly comparing those raw arrays is invalid.

`compare_fhs_and_kubo(...)` performs the compatible comparison:

1. divide FHS flux by the mesh plaquette area;
2. average Kubo density over the four corners of the corresponding periodic plaquette;
3. form the density residual;
4. report per-band L2 and Linf norms.

No independent normalization by maxima is allowed in quantitative figures or tests.

## Direct gap diagnostic

For adjacent bands \(n\) and \(n+1\), the code records

$$
\Delta_{n,n+1}^{\min}=\min_{\mathbf{k}}
[E_{n+1}(\mathbf{k})-E_n(\mathbf{k})].
$$

A nonzero result is necessary before interpreting an isolated-band Chern number or using the
interband Kubo denominator.

## Expected Harper-Hofstadter result

For the frozen `p=1`, `q=3`, `t_x=t_y=1` model and the adopted signs,

$$
(C_1,C_2,C_3)=(-1,2,-1),
\qquad \sum_n C_n=0.
$$

This is a regression target, not an excuse to force the output: both FHS and Kubo routines are
implemented independently and are tested separately.

## Continuum Dirac limitation

The massive Dirac warm-up has a well-defined local curvature but a noncompact momentum plane.
Its continuum half-integer contribution is therefore not reported as a lattice-band Chern number in
this repository.  It is used only to test the Kubo formula against an analytic local result.
