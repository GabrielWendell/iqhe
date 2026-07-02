# Edge-physics diagnostics

This note records the definitions used by the Stage-3 implementation.  It exists to prevent a
common failure mode in computational topological-matter work: calling a state an edge state only
because a plotted profile appears bright near a boundary.

## Geometry

The central ribbon has open boundaries in $x$ and periodic boundaries in $y$.  Its transverse
basis index is the Stage-1 x-site coordinate $m=0,\ldots,L_x-1$.  A strip width $w$ must satisfy
$2w\le L_x$, so left and right masks are disjoint.

## Measured quantities

- **Left participation:** probability in the first $w$ transverse sites.
- **Right participation:** probability in the last $w$ transverse sites.
- **Total edge participation:** the sum of left and right participation.
- **Edge polarization:** left minus right participation.
- **IPR:** $\sum_m |\psi_m|^4$ for a normalized eigenstate.

An eigenstate is called *edge-localized for the Stage-3 diagnostic* only after its total edge
participation crosses a declared threshold.  The threshold is a transparent numerical choice, not
a topological invariant; it is recorded in the configuration file and validation report.

## Bulk-to-boundary comparison

The Stage-2 bulk result supplies band Chern numbers.  The Stage-3 calculation uses their cumulative
sums below each gap.  In a finite ribbon, an edge branch is measured through an energy crossing at a
midgap reference energy.  The slope sign $\operatorname{sign}(dE/dk_y)$ gives its orientation.
Because the two physical boundaries face opposite directions, the corresponding left/right signed
crossing counts have opposite signs.

## What this does not establish

- It does not show time-domain chirality by itself.
- It does not show protection against arbitrary perturbations.
- It does not infer a Chern number from a visual color map.
- It does not treat a large IPR alone as evidence of an edge state; a defect-localized state may also
  have a large IPR.
