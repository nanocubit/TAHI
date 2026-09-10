"""Minimal deterministic TAHI-X spatial archive reference model."""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True, order=True)
class Coordinate:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values or any(not isfinite(value) for value in self.values):
            raise ValueError("coordinate must contain finite values")


@dataclass(frozen=True, order=True)
class CellAddress:
    values: tuple[int, ...]


@dataclass(frozen=True)
class Snapshot:
    dimensions: int
    minimum: tuple[float, ...]
    maximum: tuple[float, ...]
    grid: tuple[int, ...]
    object_count: int
    occupied_cells: int
    version: str = "tahi-x-v0.1"


@dataclass(frozen=True)
class CellDirectory:
    keys: tuple[CellAddress, ...]
    offsets: tuple[int, ...]
    counts: tuple[int, ...]
    packed_keys: tuple[int, ...] = ()
    strides: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if len(self.keys) != len(self.offsets) or len(self.keys) != len(self.counts):
            raise ValueError("directory arrays must have equal length")
        if any(offset < 0 or count < 0 for offset, count in zip(self.offsets, self.counts)):
            raise ValueError("offsets and counts must be non-negative")
        if self.packed_keys and len(self.packed_keys) != len(self.keys):
            raise ValueError("packed keys must match directory length")

    def key(self, address: CellAddress) -> int:
        if not self.strides:
            raise ValueError("directory has no packing strides")
        return sum(value * stride for value, stride in zip(address.values, self.strides))

    def posting_span(self, address: CellAddress) -> tuple[int, int] | None:
        if not self.packed_keys:
            return None
        packed = self.key(address)
        index = bisect_left(self.packed_keys, packed)
        if index >= len(self.packed_keys) or self.packed_keys[index] != packed:
            return None
        return self.offsets[index], self.counts[index]


@dataclass(frozen=True)
class PostingStore:
    object_ids: tuple[int, ...]


class Archivist:
    def __init__(self, minimum: Sequence[float], maximum: Sequence[float], grid: Sequence[int]):
        self.minimum = tuple(float(value) for value in minimum)
        self.maximum = tuple(float(value) for value in maximum)
        self.grid = tuple(int(value) for value in grid)
        if not self.minimum or len(self.minimum) != len(self.maximum) or len(self.minimum) != len(self.grid):
            raise ValueError("bounds and grid must have equal non-zero dimensions")
        if any(not isfinite(value) for value in self.minimum + self.maximum):
            raise ValueError("bounds must be finite")
        if any(hi <= lo or size <= 0 for lo, hi, size in zip(self.minimum, self.maximum, self.grid)):
            raise ValueError("invalid bounds or grid")

    def coordinate(self, values: Sequence[float]) -> Coordinate:
        coordinate = Coordinate(tuple(float(value) for value in values))
        if len(coordinate.values) != len(self.minimum):
            raise ValueError("coordinate dimension mismatch")
        if any(value < lo or value > hi for value, lo, hi in zip(coordinate.values, self.minimum, self.maximum)):
            raise ValueError("coordinate outside domain")
        return coordinate

    def cell_address(self, coordinate: Coordinate) -> CellAddress:
        cells = []
        for value, lo, hi, size in zip(coordinate.values, self.minimum, self.maximum, self.grid):
            index = size - 1 if value == hi else int((value - lo) / (hi - lo) * size)
            cells.append(max(0, min(size - 1, index)))
        return CellAddress(tuple(cells))

    def build(self, objects: Mapping[int, Sequence[float]]) -> tuple[Snapshot, CellDirectory, PostingStore, dict[int, Coordinate]]:
        records = []
        canonical = {}
        for object_id in sorted(objects):
            coordinate = self.coordinate(objects[object_id])
            canonical[object_id] = coordinate
            records.append((self.cell_address(coordinate), object_id))
        records.sort()
        strides = []
        stride = 1
        for size in reversed(self.grid):
            strides.append(stride)
            stride *= size
        strides.reverse()
        keys, offsets, counts, postings = [], [], [], []
        for cell, object_id in records:
            if not keys or keys[-1] != cell:
                keys.append(cell)
                offsets.append(len(postings))
                counts.append(0)
            postings.append(object_id)
            counts[-1] += 1
        packed_keys = tuple(sum(value * stride for value, stride in zip(key.values, strides)) for key in keys)
        snapshot = Snapshot(len(self.grid), self.minimum, self.maximum, self.grid, len(canonical), len(keys))
        directory = CellDirectory(tuple(keys), tuple(offsets), tuple(counts), packed_keys, tuple(strides))
        return snapshot, directory, PostingStore(tuple(postings)), canonical


class ExactQuery:
    def __init__(self, snapshot: Snapshot, directory: CellDirectory, postings: PostingStore, canonical: Mapping[int, Coordinate]):
        self.snapshot = snapshot
        self.directory = directory
        self.postings = postings
        self.canonical = canonical
        self.last_stats = {"retrieved_postings": 0, "exact_checks": 0, "results": 0}

    def _cell_range(self, minimum: Sequence[float], maximum: Sequence[float]) -> tuple[CellAddress, CellAddress]:
        lower, upper = [], []
        for query_lo, query_hi, domain_lo, domain_hi, size in zip(minimum, maximum, self.snapshot.minimum, self.snapshot.maximum, self.snapshot.grid):
            if query_hi < domain_lo or query_lo > domain_hi:
                return CellAddress((1,)), CellAddress((0,))
            clipped_lo = max(query_lo, domain_lo)
            clipped_hi = min(query_hi, domain_hi)
            lower.append(0 if clipped_lo <= domain_lo else min(size - 1, int((clipped_lo - domain_lo) / (domain_hi - domain_lo) * size)))
            upper.append(size - 1 if clipped_hi >= domain_hi else min(size - 1, int((clipped_hi - domain_lo) / (domain_hi - domain_lo) * size)))
        return CellAddress(tuple(lower)), CellAddress(tuple(upper))

    def range(self, minimum: Sequence[float], maximum: Sequence[float]) -> list[int]:
        if len(minimum) != self.snapshot.dimensions or len(maximum) != self.snapshot.dimensions:
            raise ValueError("query dimension mismatch")
        if any(not isfinite(float(value)) for value in tuple(minimum) + tuple(maximum)):
            raise ValueError("query bounds must be finite")
        if any(lo > hi for lo, hi in zip(minimum, maximum)):
            self.last_stats = {"retrieved_postings": 0, "exact_checks": 0, "results": 0}
            return []
        lower, upper = self._cell_range(minimum, maximum)
        candidate_ids = set()
        retrieved = 0
        left = bisect_left(self.directory.packed_keys, self.directory.key(lower))
        right = bisect_right(self.directory.packed_keys, self.directory.key(upper))
        for key_index in range(left, right):
            key = self.directory.keys[key_index]
            if all(lo <= cell <= hi for cell, lo, hi in zip(key.values, lower.values, upper.values)):
                offset, count = self.directory.offsets[key_index], self.directory.counts[key_index]
                candidate_ids.update(self.postings.object_ids[offset:offset + count])
                retrieved += count
        result = sorted(object_id for object_id in candidate_ids if all(lo <= self.canonical[object_id].values[index] <= hi for index, (lo, hi) in enumerate(zip(minimum, maximum))))
        self.last_stats = {"retrieved_postings": retrieved, "exact_checks": len(candidate_ids), "results": len(result)}
        return result
