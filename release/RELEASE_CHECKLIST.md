# Release checklist

## Metadata

- [ ] `pyproject.toml`, `src/qhe/_meta.py`, `CITATION.cff`, and `CHANGELOG.md` report the same version.
- [ ] Repository URLs contain no placeholders.
- [ ] `LICENSE` and `CITATION.cff` are present.
- [ ] Data-availability text has been reviewed for the actual release scope.
- [ ] Release notes distinguish completed results from planned work.

## Reproducibility

- [ ] Fresh-install CI is green on the supported Python matrix.
- [ ] `python scripts/run_release_smoke.py` passes locally.
- [ ] `python -m build` and `python -m twine check dist/*` pass.
- [ ] Source archive and checksum file have been generated.
- [ ] Release artifacts contain no secrets, local paths, caches, or private data.

## Publication and archive

- [ ] All contributors approve the tagged code state.
- [ ] An annotated semantic tag has been created and pushed.
- [ ] GitHub Release assets are attached and visible.
- [ ] A DOI archive has been created or is explicitly tracked as pending.
- [ ] The final DOI is inserted into `CITATION.cff` and the manuscript only after it is issued.
