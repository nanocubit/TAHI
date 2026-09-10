"""Pluggable segment readers for TAHI-X reference storage."""
from __future__ import annotations

from typing import Protocol, Sequence

from .segments import PostingSegment


class SegmentReader(Protocol):
    def read_cell_keys(self, segment_id: str) -> tuple[int, ...]: ...
    def read_offsets(self, segment_id: str) -> tuple[int, ...]: ...
    def read_object_ids(self, segment_id: str, start: int, end: int) -> tuple[int, ...]: ...


class RawSegmentReader:
    """Reader over immutable in-memory reference segments."""

    def __init__(self, segments: Sequence[PostingSegment]) -> None:
        self._segments = {segment.manifest.segment_id: segment for segment in segments}

    def _segment(self, segment_id: str) -> PostingSegment:
        try:
            return self._segments[segment_id]
        except KeyError as exc:
            raise KeyError(f"unknown segment: {segment_id}") from exc

    def read_cell_keys(self, segment_id: str) -> tuple[int, ...]:
        return self._segment(segment_id).cell_keys

    def read_offsets(self, segment_id: str) -> tuple[int, ...]:
        return self._segment(segment_id).offsets

    def read_object_ids(self, segment_id: str, start: int, end: int) -> tuple[int, ...]:
        return self._segment(segment_id).object_ids[start:end]
