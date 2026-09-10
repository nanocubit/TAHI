# TAHI-X benchmark plan

The benchmark suite will compare only explicitly defined variants. Every result must record generator version, seed, dataset parameters, query trace, exact oracle result, build time, p50/p95/p99 latency, candidate ratio, exact-check ratio, occupied cells, bytes/object, bytes/cell, peak memory, host, toolchain, and command line.

The first baseline is the pure reference model in `tahi_x/reference`. No BVH, planner, bitmap, or stored graph is included until a controlled experiment justifies it.
