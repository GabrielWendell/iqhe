# Release procedure

This document defines the public release process for IQHE. A release is a reproducible code-and-results
snapshot; it does not imply that the associated manuscript is finalized or submitted.

## Preconditions

1. The working tree is clean and all intended changes are committed.
2. `python scripts/check_release_metadata.py --tag vX.Y.Z` passes.
3. `python scripts/run_release_smoke.py` passes after an editable install with release extras.
4. `python -m build` and `python -m twine check dist/*` pass.
5. `release/RELEASE_NOTES_vX.Y.Z.md` accurately states included and excluded scope.
6. `CITATION.cff`, `CHANGELOG.md`, `README.md`, and the data-availability text are synchronized.

## Create the tag

For the Stage 5 baseline:

```bash
python scripts/create_release_tag.py --tag v0.6.0
# Review the tag, then publish it:
git push origin v0.6.0
```

The helper refuses a dirty tree by default and checks that the tag matches the version in
`pyproject.toml`, `qhe.__version__`, and `CITATION.cff`.

## GitHub release automation

Pushing a semantic tag invokes `.github/workflows/release.yml`. The workflow performs a fresh
installation, executes tests and notebooks, regenerates figures, creates a source archive and Python
distributions, writes checksums, and publishes a GitHub Release with those assets.

## DOI archive

After the GitHub release exists, create an archival record with a DOI-issuing repository such as Zenodo.
Then update the release metadata and manuscript statements with the DOI before final publication. Do not
invent a DOI or describe one as assigned until the archive service has issued it.
