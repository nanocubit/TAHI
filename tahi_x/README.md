# TAHI Iteration Archive

This directory collects source, benchmark, and report artifacts from TAHI iterations X1 through X10.2.

## Layout

- `src/`: implementation sources and native libraries' source code.
- `benchmarks/`: machine-readable benchmark results.
- `reports/`: evolution, validation, and comparison reports.

## Iteration map

- X1: brute-force baseline.
- X7: grid index.
- X9.3: compressed TAHI prototype.
- X9.5: distributed experiments; not production-ready.
- X10.0: production single-node release.
- X10.1: low-level CPU optimization.
- X10.2: BVH-based exact pruning for 10M objects.

## Correctness

Results marked exact were checked against an independent brute-force oracle for the recorded benchmark queries. Semantic extraction accuracy is separate from index correctness.

## Reproducibility

Benchmark files record dataset size, dimensionality, grid configuration, build time, query latency, result counts, and error counts where available. Hardware and compiler details should be added for a fully reproducible performance comparison.
