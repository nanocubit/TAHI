import pytest

from tahi_x.reference.segmented import SegmentedReferenceIndex
from tahi_x.reference.storage import RawSegmentReader


def test_raw_reader_exposes_segment_columns_and_ranges():
    index = SegmentedReferenceIndex.build(
        [10, 20, 30],
        [0, 2, 3, 6],
        [4, 5, 8, 9, 10, 11],
        cells_per_segment=2,
    )
    reader = RawSegmentReader(index.segments)
    segment_id = index.segments[1].manifest.segment_id

    assert reader.read_cell_keys(segment_id) == (30,)
    assert reader.read_offsets(segment_id) == (0, 3)
    assert reader.read_object_ids(segment_id, 0, 2) == (9, 10)


def test_raw_reader_rejects_unknown_segments():
    reader = RawSegmentReader(())
    with pytest.raises(KeyError, match="unknown segment"):
        reader.read_cell_keys("seg-9999")
