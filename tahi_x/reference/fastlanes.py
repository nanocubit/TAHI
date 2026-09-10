"""Optional FastLanes-backed segment reader boundary.

The native binding is intentionally optional. This module defines the stable
Python boundary without silently pretending that raw tuples are FastLanes.
"""
from __future__ import annotations

from .storage import SegmentReader


class FastLanesUnavailable(RuntimeError):
    """Raised when the optional FastLanes native binding is not installed."""


class FastLanesSegmentReader:
    """Adapter boundary for a future native FastLanes reader.

    ``native_reader`` must expose the three SegmentReader operations. The
    adapter deliberately does not fall back to RawSegmentReader, so callers
    cannot mistake an uncompressed reference path for FastLanes execution.
    """

    def __init__(self, native_reader: SegmentReader | None = None) -> None:
        if native_reader is None:
            raise FastLanesUnavailable(
                "FastLanes native binding is not installed; use RawSegmentReader"
            )
        self._native_reader = native_reader

    def read_cell_keys(self, segment_id: str) -> tuple[int, ...]:
        return tuple(self._native_reader.read_cell_keys(segment_id))

    def read_offsets(self, segment_id: str) -> tuple[int, ...]:
        return tuple(self._native_reader.read_offsets(segment_id))

    def read_object_ids(self, segment_id: str, start: int, end: int) -> tuple[int, ...]:
        return tuple(self._native_reader.read_object_ids(segment_id, start, end))
