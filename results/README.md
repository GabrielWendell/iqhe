# Numerical results

This directory stores small, reproducible result summaries and metadata.

Recommended organization:

```text
results/
├── tables/          # CSV/Parquet summaries used in manuscript tables
├── validation/      # Chern convergence, residual norms, norm-conservation logs
├── metadata/        # Run manifest, parameters, git revision, environment summary
└── generated/       # Large local outputs; ignored by Git
```

Every saved production result should identify the model parameters, numerical mesh/system size, tolerance, source script, and generating git revision.
