from __future__ import annotations

import argparse
import json
import platform
import random
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

from tahi_x.reference import Archivist, ExactQuery


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    index = (len(values) - 1) * q
    lower, upper = int(index), min(int(index) + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (index - lower)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--objects", type=int, default=100_000)
    parser.add_argument("--dimensions", type=int, default=5)
    parser.add_argument("--grid", type=int, default=16)
    parser.add_argument("--queries", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    objects = {object_id: tuple(rng.random() for _ in range(args.dimensions)) for object_id in range(args.objects)}
    archivist = Archivist((0.0,) * args.dimensions, (1.0,) * args.dimensions, (args.grid,) * args.dimensions)

    tracemalloc.start()
    start = time.perf_counter()
    snapshot, directory, postings, canonical = archivist.build(objects)
    build_seconds = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    query_engine = ExactQuery(snapshot, directory, postings, canonical)
    tahi_times, brute_times = [], []
    candidate_ratios, false_negatives, false_positives = [], 0, 0
    for _ in range(args.queries):
        lo = tuple(rng.random() * 0.8 for _ in range(args.dimensions))
        width = tuple(rng.random() * 0.2 for _ in range(args.dimensions))
        hi = tuple(min(1.0, value + delta) for value, delta in zip(lo, width))
        start = time.perf_counter()
        result = query_engine.range(lo, hi)
        tahi_times.append((time.perf_counter() - start) * 1000)
        start = time.perf_counter()
        expected = sorted(object_id for object_id, point in objects.items() if all(low <= value <= high for value, low, high in zip(point, lo, hi)))
        brute_times.append((time.perf_counter() - start) * 1000)
        result_set, expected_set = set(result), set(expected)
        false_negatives += len(expected_set - result_set)
        false_positives += len(result_set - expected_set)
        candidate_ratios.append(len(result) / max(1, len(objects)))

    report = {
        "benchmark": "tahi-x-reference-v0.1",
        "objects": args.objects,
        "dimensions": args.dimensions,
        "grid": args.grid,
        "queries": args.queries,
        "seed": args.seed,
        "occupied_cells": snapshot.occupied_cells,
        "build_ms": build_seconds * 1000,
        "tahi_ms": {"mean": statistics.mean(tahi_times), "p50": percentile(tahi_times, 0.50), "p95": percentile(tahi_times, 0.95), "p99": percentile(tahi_times, 0.99)},
        "brute_ms": {"mean": statistics.mean(brute_times), "p50": percentile(brute_times, 0.50), "p95": percentile(brute_times, 0.95), "p99": percentile(brute_times, 0.99)},
        "candidate_ratio_mean": statistics.mean(candidate_ratios),
        "false_negatives": false_negatives,
        "false_positives": false_positives,
        "peak_tracemalloc_bytes": peak_bytes,
        "python": sys.version,
        "platform": platform.platform(),
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
