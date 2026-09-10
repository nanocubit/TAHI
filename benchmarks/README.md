# TAHI-X benchmark plan

The benchmark suite compares only explicitly defined variants. Every result records generator version, seed, dataset parameters, query trace parameters, exact oracle result, build time, p50/p95/p99 latency, retrieved postings, exact checks, candidate ratio, candidate amplification, occupied cells, peak traced memory, false positives, false negatives, host, interpreter, and command line.

The candidate ratio is `retrieved_postings / objects`. Candidate amplification is `exact_checks / final_results`; queries with no results are reported separately in future benchmark versions.

## Local run

```bash
python -m benchmarks.tahi_x_baseline --objects 100000 --queries 100 --seed 42 --output benchmark-results/run.json
```

The first baseline is the pure reference model in `tahi_x/reference`. No BVH, planner, bitmap, or stored graph is included until a controlled experiment justifies it.
