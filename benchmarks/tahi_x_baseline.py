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

WIDTHS = {"narrow": 0.02, "medium": 0.10, "wide": 0.30}


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
    parser.add_argument("--query-width", choices=sorted(WIDTHS), default="medium")
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
    candidate_ratios, amplification = [], []
    empty_queries = 0
    total_retrieved, total_exact_checks, total_results = 0, 0, 0
    false_negatives, false_positives = 0, 0
    width = WIDTHS[args.query_width]
    for _ in range(args.queries):
        lo = tuple(rng.random() * (1.0 - width) for _ in range(args.dimensions))
        hi = tuple(value + width for value in lo)
        start = time.perf_counter()
        result = query_engine.range(lo, hi)
        tahi_times.append((time.perf_counter() - start) * 1000)
        stats = query_engine.last_stats
        total_retrieved += stats["retrieved_postings"]
        total_exact_checks += stats["exact_checks"]
        total_results += stats["results"]
        candidate_ratios.append(stats["retrieved_postings"] / max(1, args.objects))
        if stats["results"] == 0:
            empty_queries += 1
        else:
            amplification.append(stats["exact_checks"] / stats["results"])
        start = time.perf_counter()
        expected = sorted(object_id for object_id, point in objects.items() if all(low <= value <= high for value, low, high in zip(point, lo, hi)))
        brute_times.append((time.perf_counter() - start) * 1000)
        result_set, expected_set = set(result), set(expected)
        false_negatives += len(expected_set - result_set)
        false_positives += len(result_set - expected_set)

    report = {
        "benchmark": "tahi-x-reference-v0.1",
        "objects": args.objects,
        "dimensions": args.dimensions,
        "grid": args.grid,
        "queries": args.queries,
        "seed": args.seed,
        "query_width": args.query_width,
        "query_width_per_dimension": width,
        "query_volume": width ** args.dimensions,
        "occupied_cells": snapshot.occupied_cells,
        "build_ms": build_seconds * 1000,
        "tahi_ms": {"mean": statistics.mean(tahi_times), "p50": percentile(tahi_times, 0.50), "p95": percentile(tahi_times, 0.95), "p99": percentile(tahi_times, 0.99)},
        "brute_ms": {"mean": statistics.mean(brute_times), "p50": percentile(brute_times, 0.50), "p95": percentile(brute_times, 0.95), "p99": percentile(brute_times, 0.99)},
        "candidate_ratio_mean": statistics.mean(candidate_ratios),
        "candidate_amplification_mean_non_empty": statistics.mean(amplification) if amplification else None,
        "empty_queries": empty_queries,
        "total_retrieved_postings": total_retrieved,
        "total_exact_checks": total_exact_checks,
        "total_results": total_results,
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
