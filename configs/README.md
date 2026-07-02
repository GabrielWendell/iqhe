# Configurations

Version-controlled TOML files record named, reproducible model and validation parameter sets.

- `harper_hofstadter_phi_1_3.toml` is the Stage-1 Hamiltonian baseline for the central teaching case.
- `topology_validation_phi_1_3.toml` records the Stage-2 mesh series, topological regression target,
  numerical tolerances, and direct-gap acceptance criteria.
- `edge_validation_phi_1_3.toml` records the Stage-3 bulk mesh, ribbon size, edge-strip width,
  edge-participation threshold, and side-resolved crossing targets.

A configuration file may select parameters but may not override the conventions frozen in
`docs/CONVENTIONS.md` without a new accepted decision-log entry.
