# TAHI / Archivarius forensic audit v0.1

## Scope

This audit establishes the baseline for the current `main` tree. It covers the repository structure, the C++ TAHI X10.2 BVH prototype, Archivarius ingestion, schemas, tests, CI, and benchmark reproducibility.

## Current implementation

- `tahi_x/src/tahi_x10_2_bvh.cpp` is the principal TAHI runtime artifact visible in the repository.
- Archivarius currently contains ingestion helpers for Kaggle download, provenance manifest generation, checksum validation, and optional GCS upload.
- JSON Schema files define claim, entity, and relation records.
- `.github/workflows/archivarius-kaggle-ingestion.yml` provides manual and scheduled ingestion orchestration.

## Findings

### P0 — baseline test reliability

The test suite previously used an incorrect SHA-256 expectation for the bytes `archivarius`. The correct digest is `88775190664d3d6a6debb2a4d060b6ae1986078b0a7855c38f6e988d57eee217`. The package was also missing a project configuration, making clean pytest collection dependent on the caller's `PYTHONPATH`.

### P1 — runtime boundary is incomplete

The repository does not yet expose a complete TAHI production API, persistence format, snapshot metadata, update/delete semantics, bindings, or a canonical-store-to-index implementation boundary. The C++ BVH should therefore be treated as a reference prototype, not as a finished engine.

### P1 — memory model risk

The dense allocation strategy `grid^5` creates a large number of vector objects before occupied cells are materialized. Future designs should benchmark a sparse occupied-cell directory with sorted cell IDs, offsets, and contiguous postings against the current cell-vector layout.

### P1 — benchmark reproducibility

Benchmark artifacts must record generator version, seed, query trace, dataset parameters, compiler/toolchain, host metadata, peak RSS, index size, and oracle agreement before claims such as “scales to 10M” are generalized.

### P1 — schema and architecture alignment

The Archivarius documentation and JSON Schemas need one shared provenance contract, explicit schema versioning, and consistent semantics for observation, claim, relation, entity, and object values.

### P2 — operational hardening

The scheduled Kaggle workflow depends on repository variables for dataset, version, and bucket. These assumptions should be validated explicitly and documented before enabling production schedules.

## Target reference architecture

```text
Canonical Store
  -> Archivist
  -> Cell Address / Occupied Cell Directory / Contiguous Postings
  -> TAHI Snapshot
  -> Cell Routing / BVH / Local Index
  -> Exact Verification
```

The BVH is an operator in the index pipeline, not the complete TAHI architecture.

## Next steps

1. Keep the baseline tests green in CI.
2. Define canonical record and provenance contracts.
3. Add a deterministic Archivist reference implementation.
4. Add a benchmark generator and exact oracle.
5. Measure memory and snapshot size.
6. Freeze semantics before any Rust rewrite.
