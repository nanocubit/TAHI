# TAHI-X benchmark plan

The benchmark suite compares only explicitly defined variants. Every result records generator version, seed, dataset parameters, query trace parameters, exact oracle result, build time, p50/p95/p99 latency, candidate ratio, occupied cells, peak traced memory, false positives, false negatives, host, interpreter, and command line.

## Local run

```bash
python benchmarks/tahi_x_baseline.py --objects 100000 --queries 100 --seed 42 --output benchmark-results/run.json
```

## CI run

Use the `TAHI-X reproducible baseline` workflow with `workflow_dispatch`. The workflow runs tests, executes the reference benchmark, and stores the JSON result as an artifact.

The first baseline is the pure reference model in `tahi_x/reference`. No BVH, planner, bitmap, or stored graph is included until a controlled experiment justifies it.
