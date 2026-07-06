# Manuscript Figure Captions

These captions are manuscript-ready working text. Update only through pull-requested source edits,
not by embedding prose inside exported graphics.

## Figure 1 — Computational route from bulk geometry to edge transport

**Conceptual roadmap for the computational article.** Berry curvature first characterizes the local
geometry of a Bloch band in momentum space. Its Brillouin-zone integral gives the Chern number,
which predicts the net chirality of boundary branches in a ribbon spectrum. In the later dynamics
stage, an edge-projected wave packet will convert this static bulk-boundary statement into a
real-space transport observable. The present Stage-4 release implements the first three validated
links and reserves the time-domain panels for the dynamics stage.

## Figure 2 — Gauge-invariant FHS plaquette

**Oriented momentum-space plaquette used by the Fukui–Hatsugai–Suzuki (FHS) algorithm.** The
normalized overlap links are evaluated around the oriented loop
\(\mathbf{k}\to\mathbf{k}+\hat 1\to\mathbf{k}+\hat 1+\hat 2\to\mathbf{k}+\hat 2\to\mathbf{k}\).
With the frozen convention \(\mathbf A=i\langle u|\nabla_{\mathbf k}u\rangle\), the displayed
oriented product is negated so that the discrete plaquette flux approaches the Berry-curvature
density used throughout the repository. Summing the fluxes over the periodic magnetic Brillouin
zone yields an integer band Chern number.

## Figure 3 — Massive Dirac warm-up

**Massive two-band Dirac warm-up with \(v_F=1\) and \(\Delta=0.25\).** (a) The spectrum along
\(k_y=0\) exhibits a gap \(2|\Delta|\). (b) The lower-band Berry curvature along the same line is
localized near the avoided crossing. (c) The full lower-band curvature on a square momentum window
is rotationally symmetric around the Dirac point. This continuum result illustrates local geometric
curvature but is not itself a lattice-band Chern number because the momentum domain is noncompact.

## Figure 4 — Harper–Hofstadter magnetic subbands

**Harper–Hofstadter subbands for flux \(\phi=1/3\) along a closed path in the magnetic Brillouin
zone.** The three magnetic subbands arise from the three-site magnetic unit cell in Landau gauge.
The legend reports the FHS Chern numbers obtained independently in the Stage-2 validation,
\((C_1,C_2,C_3)=(-1,2,-1)\), under the frozen sign convention. The gaps between these bands are
the bulk energy intervals used in the finite-ribbon bulk-boundary diagnosis.

## Figure 5 — Compatible FHS and interband-Kubo validation

**Numerical validation of Berry-curvature and Chern calculations for the lowest
Harper–Hofstadter band at $\phi=1/3$.** (a) FHS curvature density, (b) the interband-Kubo
curvature averaged over matching plaquettes, and (c) their residual are plotted on the same
magnetic-Brillouin-zone mesh. The first-row FHS and Kubo panels use a common colour normalization;
the residual panel uses a symmetric normalization about zero. (d) FHS and Kubo Chern estimates
converge to the same integer band sequence with mesh refinement. (e,f) The corresponding $L^2$
and $L^\infty$ curvature residual norms decrease under refinement. No independent rescaling is
applied to visually enhance agreement.

## Figure 6 — Quantitative bulk-boundary correspondence

**Finite-ribbon evidence for bulk-boundary correspondence at $\phi=1/3$.** (a) The x-open,
y-periodic ribbon spectrum is coloured by the measured total edge participation of every
eigenstate. Dashed lines mark the midpoints of the positive global bulk gaps, while open triangles
mark edge-localized reference-energy crossings; triangle orientation encodes the sign of the branch
slope. (b) Representative crossing-state probability profiles demonstrate localization on the Left
or Right boundary. The side-resolved oriented crossing counts reproduce the cumulative gap Chern
numbers under the frozen convention.
