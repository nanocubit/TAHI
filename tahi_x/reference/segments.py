"""Reference segmented storage primitives for TAHI-X.

The module deliberately keeps storage semantics simple and deterministic. It
segments sorted cell postings by cell-key ranges without changing query
semantics or imposing a binary format.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable, Sequence


@dataclass(frozen=True)
class SegmentManifest:
    segment_id: str
    cell_min: int
    cell_max: int
    posting_start: int
    posting_end: int
    cell_count: int
    posting_count: int
    digest: str
    format: str = "raw-v1"

    def to_dict(self) -> dict[str, object]:
        return {
            "segment_id": self.segment_id,
            "cell_min": self.cell_min,
            "cell_max": self.cell_max,
            "posting_start": self.posting_start,
            "posting_end": self.posting_end,
            "cell_count": self.cell_count,
            "posting_count": self.posting_count,
            "digest": self.digest,
            "format": self.format,
        }


@dataclass(frozen=True)
class PostingSegment:
    manifest: SegmentManifest
    cell_keys: tuple[int, ...]
    offsets: tuple[int, ...]
    object_ids: tuple[int, ...]

    def read_cell(self, cell_key: int) -> tuple[int, ...]:
        try:
            index = self.cell_keys.index(cell_key)
        except ValueError:
            return ()
        start = self.offsets[index]
        end = self.offsets[index + 1]
        return self.object_ids[start:end]


def _digest(cell_keys: Sequence[int], offsets: Sequence[int], object_ids: Sequence[int]) -> str:
    payload = json.dumps(
        {
            "cell_keys": list(cell_keys),
            "offsets": list(offsets),
            "object_ids": list(object_ids),
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def build_segments(
    cell_keys: Sequence[int],
    offsets: Sequence[int],
    object_ids: Sequence[int],
    *,
    cells_per_segment: int,
) -> tuple[PostingSegment, ...]:
    """Build deterministic segments from sorted cell keys and postings.

    ``offsets`` must contain one entry per cell plus a final postings end
    offset. Empty segments are not emitted. The input arrays are copied into
    immutable tuples; the source arrays are never modified.
    """
    if cells_per_segment <= 0:
        raise ValueError("cells_per_segment must be positive")
    if len(offsets) != len(cell_keys) + 1:
        raise ValueError("offsets must have len(cell_keys) + 1 entries")
    if offsets[0] != 0 or offsets[-1] != len(object_ids):
        raise ValueError("offsets must start at 0 and end at len(object_ids)")
    if any(left > right for left, right in zip(offsets, offsets[1:])):
        raise ValueError("offsets must be non-decreasing")
    if any(left > right for left, right in zip(cell_keys, cell_keys[1:])):
        raise ValueError("cell_keys must be sorted")

    result: list[PostingSegment] = []
    for start_cell in range(0, len(cell_keys), cells_per_segment):
        end_cell = min(start_cell + cells_per_segment, len(cell_keys))
        base = offsets[start_cell]
        end = offsets[end_cell]
        keys = tuple(cell_keys[start_cell:end_cell])
        local_offsets = tuple(value - base for value in offsets[start_cell:end_cell + 1])
        ids = tuple(object_ids[base:end])
        manifest = SegmentManifest(
            segment_id=f"seg-{len(result):04d}",
            cell_min=keys[0],
            cell_max=keys[-1],
            posting_start=base,
            posting_end=end,
            cell_count=len(keys),
            posting_count=len(ids),
            digest=_digest(keys, local_offsets, ids),
        )
        result.append(PostingSegment(manifest, keys, local_offsets, ids))
    return tuple(result)


def query_segments(
    segments: Iterable[PostingSegment],
    cell_keys: Iterable[int],
) -> tuple[int, ...]:
    """Return sorted unique postings for the requested cell keys."""
    wanted = tuple(cell_keys)
    result: set[int] = set()
    for segment in segments:
        if not wanted or segment.manifest.cell_max < min(wanted) or segment.manifest.cell_min > max(wanted):
            continue
        for key in wanted:
            result.update(segment.read_cell(key))
    return tuple(sorted(result))
