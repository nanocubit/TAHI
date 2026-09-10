# TAHI Final Laboratory Report

## Scope

TAHI evolved from a brute-force baseline to an exact multidimensional range index with grid partitioning and BVH pruning. Archivarius is the broader multimodal knowledge and provenance layer; TAHI is its derived exact index.

## Iterations

- X1: brute-force baseline.
- X7: grid index.
- X9.3: compressed single-node prototype.
- X9.5: distributed experiments; hash and cell sharding were not accepted as production designs because routing and global cell semantics were unresolved.
- X10.0: production single-node release.
- X10.1: CPU-level optimization.
- X10.2: BVH exact pruning.

## Recorded benchmarks

### X10.0, 100K objects

- 5 dimensions, grid 32.
- Uniform/isotropic mean: 1.251 ms.
- Uniform/axis0 mean: 0.697 ms.
- Correctness: zero false negatives and false positives in the recorded tests.

### X10.2, 10M objects

- 5 dimensions, grid 32.
- Build: 22.14 seconds.
- Occupied cells: 8,647,640.
- Best recorded mean: 2.51 ms at selectivity 0.001, anisotropic shape.
- Selectivity 0.01: 5.54–7.86 ms mean across recorded shapes.
- Selectivity 0.1: 22.28–32.15 ms mean.
- Correctness: 180 queries checked, zero false negatives and zero false positives.

## Interpretation

These are exact predicate results for the recorded workloads. They do not imply semantic correctness of upstream feature extractors, nor universal performance on all hardware or distributions.

## Limitations

The current implementation is fixed to five float dimensions and uses a dense grid-bin allocation. Streaming updates, distributed execution, GPU execution, typed schemas, and high-dimensional sparse indexing remain future work.

## Next steps

- Generalize dimensions and typed feature schemas.
- Replace dense bins with sparse/CSR storage.
- Add SIMD and parallel query execution.
- Add GPU build and query kernels while preserving oracle validation.
- Integrate with Archivarius canonical records and provenance.
