# Dependency snapshots

This directory complements, but does not replace, `pyproject.toml` and `environment.yml`.

- `release-environment-py313.txt` is the exact direct-package snapshot used in the Stage 5 validation
  environment.
- Use `python scripts/export_environment_snapshot.py` after creating a new release environment to record
  a platform-specific snapshot.

Scientific Python wheels are platform- and interpreter-specific. Consequently, this repository records a
transparent tested snapshot rather than claiming that one lock file is portable across every operating
system and Python minor version.
