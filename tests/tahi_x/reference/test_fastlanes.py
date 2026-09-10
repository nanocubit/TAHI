import pytest

from tahi_x.reference.fastlanes import FastLanesSegmentReader, FastLanesUnavailable


def test_fastlanes_backend_is_explicitly_optional():
    with pytest.raises(FastLanesUnavailable, match="native binding is not installed"):
        FastLanesSegmentReader()


def test_fastlanes_adapter_forwards_native_reader():
    class NativeReader:
        def read_cell_keys(self, segment_id):
            return [10, 20]

        def read_offsets(self, segment_id):
            return [0, 2, 3]

        def read_object_ids(self, segment_id, start, end):
            return [4, 5, 8][start:end]

    reader = FastLanesSegmentReader(NativeReader())
    assert reader.read_cell_keys("seg-0000") == (10, 20)
    assert reader.read_offsets("seg-0000") == (0, 2, 3)
    assert reader.read_object_ids("seg-0000", 0, 2) == (4, 5)
