# TAHI and Competitor Positioning

## Important distinction

TAHI performs exact multidimensional range predicates. FAISS, HNSW, ScaNN, Annoy, Milvus, and Elasticsearch configurations commonly target approximate nearest-neighbor or broader vector-search workloads. Direct latency comparisons are meaningful only after matching hardware, dataset, query semantics, recall definition, index parameters, and hardware.

## TAHI strengths

- Exact predicate semantics for the indexed features.
- No recall trade-off in the verified benchmark workload.
- Strong fit for low-dimensional structured attributes and range filters.
- Simple batch-build and query model.
- BVH pruning scales better than the earlier flat cell scan on selective queries.

## TAHI gaps

- Current implementation is fixed to five float dimensions.
- No production streaming updates.
- No accepted distributed implementation yet.
- No GPU implementation yet.
- No complete vector-database feature set.
- Semantic feature quality remains the responsibility of upstream extractors.

## Position

TAHI should be positioned as an exact low-dimensional multidimensional range engine and as the exact indexing layer for Archivarius. It should not be marketed as a replacement for high-dimensional approximate-nearest-neighbor systems.

## Next comparison protocol

A fair benchmark must publish dataset, hardware, compiler, index parameters, build time, query distribution, result cardinality, recall/precision, memory, and update workload. Until that protocol is run, competitor numbers are directional rather than authoritative.
