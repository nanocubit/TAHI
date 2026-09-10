"""Reference query adapter backed by deterministic posting segments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .segments import PostingSegment, build_segments, query_segments


@dataclass(frozen=True)
class SegmentedReferenceIndex:
    """Small reference index preserving the existing cell-to-postings contract."""

    segments: tuple[PostingSegment, ...]

    @classmethod
    def build(
        cls,
        cell_keys: Sequence[int],
        offsets: Sequence[int],
        object_ids: Sequence[int],
        *,
        cells_per_segment: int,
    ) -> "SegmentedReferenceIndex":
        return cls(build_segments(
            cell_keys,
            offsets,
            object_ids,
            cells_per_segment=cells_per_segment,
        ))

    def query_cells(self, cell_keys: Iterable[int]) -> tuple[int, ...]:
        return query_segments(self.segments, cell_keys)

    def manifests(self) -> tuple[dict[str, object], ...]:
        return tuple(segment.manifest.to_dict() for segment in self.segments)
