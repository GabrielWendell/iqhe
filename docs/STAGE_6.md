# Stage 6 implementation record — chiral dynamics and velocity/defect validation

Stage 6 completes the validated computational chain needed for the EJP paper by adding measurable
time-domain edge dynamics to the static bulk-boundary correspondence established in Stage 3.

## Added source modules

- `src/qhe/dynamics/packets.py` — normalized Gaussian edge seeds and phase-preserving projection
  onto a selected edge eigenspace.
- `src/qhe/dynamics/evolution.py` — spectral unitary evolution and norm diagnostics.
- `src/qhe/dynamics/observables.py` — edge probability, bulk leakage, centroid/edge-coordinate
  motion, and velocity fitting.
- `src/qhe/dynamics/currents.py` — local Harper-Hofstadter bond-current diagnostics.
- `src/qhe/dynamics/defects.py` — controlled weak-link boundary defects.
- `src/qhe/dynamics/analysis.py` — clean and defect Stage-6 validation workflow.
- `src/qhe/viz/dynamics.py` — manuscript figure builders for Figures 7 and 8.

The boundary geometry layer now also exposes `open_side_masks`, which provides left, right, top,
bottom, and perimeter masks for fully open lattices.

## Added configuration, scripts, and tests

- `configs/dynamics_validation_phi_1_3.toml`
- `scripts/run_stage6_checks.py`
- `scripts/make_stage6_figures.py`
- `tests/test_dynamics.py`
- `tests/test_open_side_masks.py`

## Default validation result

The frozen validation case uses $\phi=1/3$, the left edge of the lower bulk gap, a fully open
$12\times 30$ finite lattice, and a single weakened boundary link.  The default run gives a
clean packet velocity close to the ribbon branch group velocity and keeps the packet largely on
the boundary in both the clean and defect systems.

The acceptance gates are configured in `configs/dynamics_validation_phi_1_3.toml` and include norm
conservation, initial edge probability, mean clean/defect edge probability, velocity agreement, and
the sign of the edge-current diagnostic.

## Figure status

Figures 7 and 8 are now implemented:

- `figure_07_chiral_dynamics` — shared-scale snapshots, edge/bulk probabilities, edge coordinate,
  and current direction.
- `figure_08_velocity_and_defect` — group/packet velocity comparison, edge retention, and weak-link
  defect routing.

They are rendered by the Stage-6-specific figure script rather than the static Stage-4 renderer.
