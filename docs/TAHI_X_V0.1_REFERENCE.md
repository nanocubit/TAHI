# TAHI-X v0.1 Reference Specification

## Status

Research/reference specification. This document defines semantics before optimization. It does not claim production readiness or benchmark superiority.

## Scope

TAHI-X v0.1 is a rebuildable spatial archive index over canonical objects. The canonical store remains authoritative; the index is disposable and versioned by snapshot metadata.

The initial implementation intentionally excludes BVH, planner, bitmap indexes, stored adjacency graphs, persistence, updates, deletes, and Rust bindings.

## Primitives

### Coordinate

A coordinate is an ordered tuple of finite real values with fixed dimension `D`. v0.1 uses a uniform numeric domain `[min_d, max_d]` per dimension and rejects NaN and infinity.

### CellAddress

A cell address is an ordered tuple `(c0, ..., c[D-1])`. Each component is an integer in `[0, grid_d - 1]`. The address is a spatial identity, not a stored graph vertex.

### CellDirectory

The directory stores sorted occupied cell keys and ranges into the posting store. It must not allocate one container per possible cell.

### PostingStore

The posting store is a contiguous sequence of canonical object IDs grouped by sorted cell key. Object order inside a posting is deterministic.

### Snapshot

A snapshot records dimension, domain bounds, grid shape, object count, occupied-cell count, and implementation/schema version. It can be rebuilt from canonical data.

## Archive semantics

`ARCHIVE(objects)` normalizes each object, computes its coordinate and cell address, sorts records by cell key, and emits a directory plus contiguous postings. Canonical objects are not copied into the index except for IDs and the metadata required for verification.

## Query semantics

`QUERY(predicate)` computes the conservative range of cells intersecting the predicate, retrieves postings for occupied cells in that range, deduplicates candidate IDs, and applies the exact predicate to canonical coordinates. False positives are permitted before verification; false negatives are forbidden.

The reference invariant is:

```text
QUERY_TAHI_X(q, ARCHIVE(objects)) == BRUTE_FORCE(objects, q)
```

Results are compared as deterministic sorted canonical IDs.

## Measurements

Every experiment should record build time, query p50/p95/p99, candidate ratio, exact-check ratio, occupied cells, bytes/object, bytes/cell, peak memory, false positives, false negatives, seed, generator version, host, compiler/interpreter, and command line.

## Excluded until experiments justify them

BVH, planner, bitmap acceleration, stored neighborhood graph, multiple resolutions, persistence format, streaming updates, deletes, semantic/time address layers, and Rust implementation.
