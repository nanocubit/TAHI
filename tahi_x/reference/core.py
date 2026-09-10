"""Minimal deterministic TAHI-X spatial archive reference model."""
from __future__ import annotations

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

    def __post_init__(self) -> None:
        if len(self.keys) != len(self.offsets) or len(self.keys) != len(self.counts):
            raise ValueError("directory arrays must have equal length")
        if any(offset < 0 or count < 0 for offset, count in zip(self.offsets, self.counts)):
            raise ValueError("offsets and counts must be non-negative")


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
        keys, offsets, counts, postings = [], [], [], []
        for cell, object_id in records:
            if not keys or keys[-1] != cell:
                keys.append(cell)
                offsets.append(len(postings))
                counts.append(0)
            postings.append(object_id)
            counts[-1] += 1
        snapshot = Snapshot(len(self.grid), self.minimum, self.maximum, self.grid, len(canonical), len(keys))
        return snapshot, CellDirectory(tuple(keys), tuple(offsets), tuple(counts)), PostingStore(tuple(postings)), canonical


class ExactQuery:
    def __init__(self, snapshot: Snapshot, directory: CellDirectory, postings: PostingStore, canonical: Mapping[int, Coordinate]):
        self.snapshot = snapshot
        self.directory = directory
        self.postings = postings
        self.canonical = canonical

    def range(self, minimum: Sequence[float], maximum: Sequence[float]) -> list[int]:
        if len(minimum) != self.snapshot.dimensions or len(maximum) != self.snapshot.dimensions:
            raise ValueError("query dimension mismatch")
        if any(lo > hi for lo, hi in zip(minimum, maximum)):
            return []
        candidate_ids = set()
        for key, offset, count in zip(self.directory.keys, self.directory.offsets, self.directory.counts):
            if all(lo <= cell <= hi for cell, lo, hi in zip(key.values, minimum, maximum)):
                candidate_ids.update(self.postings.object_ids[offset:offset + count])
        return sorted(object_id for object_id in candidate_ids if all(lo <= self.canonical[object_id].values[index] <= hi for index, (lo, hi) in enumerate(zip(minimum, maximum))))
