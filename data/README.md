# Data policy

The current project uses model-generated numerical data. No external research dataset is required for Stage 0.

## Directory conventions

```text
raw/       Immutable external inputs, if ever introduced.
interim/   Derived but non-final temporary products.
processed/ Stable analysis-ready numerical products.
external/  Non-redistributable or separately licensed material.
```

None of these directories should be created or populated casually. Any future external input must be documented with:

- provenance and license;
- checksum where practical;
- acquisition date;
- transformation history;
- relationship to generated results.
