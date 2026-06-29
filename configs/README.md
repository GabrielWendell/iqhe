# Configuration files

This directory will hold small, version-controlled parameter files used by scripts and notebooks.

Examples planned for later stages:

```text
hofstadter_phi_1_3.toml
mesh_convergence.toml
ribbon_default.toml
dynamics_packet.toml
defect_test.toml
```

Physical conventions are not ordinary runtime settings. They must first be recorded and approved in `docs/CONVENTIONS.md`.

Version-controlled TOML files record named, reproducible model and validation parameter sets.
`harper_hofstadter_phi_1_3.toml` is the Stage-1 baseline for the central teaching case.

A configuration file may select parameters but may not override the conventions frozen in
`docs/CONVENTIONS.md` without a new accepted decision-log entry.