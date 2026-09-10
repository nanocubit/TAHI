# TAHI-X benchmark plan

The benchmark matrix compares the reference model across object counts, grid sizes, random seeds, and query widths. Every result records dataset/query parameters, build time, p50/p95/p99 latency, retrieved postings, exact checks, candidate ratio, non-empty candidate amplification, occupied cells, memory, correctness, host, interpreter, and command line.

## Matrix

- Objects: 10K, 100K, 1M.
- Grid: 8, 16, 32 per dimension.
- Seeds: 1, 2, 3.
- Query widths: narrow `0.02`, medium `0.10`, wide `0.30` per dimension.

The full matrix has 81 runs. Use the workflow inputs to run a single object count or seed override when validating locally. The 1M/32/wide combinations may be memory-intensive in pure Python.

## Local run

```bash
python -m benchmarks.tahi_x_baseline --objects 100000 --grid 16 --queries 100 --seed 42 --query-width medium --output benchmark-results/run.json
```

No BVH, planner, bitmap, or stored graph is included until a controlled experiment justifies it.
