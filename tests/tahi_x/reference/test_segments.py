from tahi_x.reference.segments import build_segments, query_segments


def test_build_segments_preserves_postings_and_manifest_ranges():
    segments = build_segments(
        [10, 20, 30],
        [0, 2, 3, 6],
        [4, 5, 8, 9, 10, 11],
        cells_per_segment=2,
    )

    assert len(segments) == 2
    assert segments[0].manifest.cell_min == 10
    assert segments[0].manifest.cell_max == 20
    assert segments[0].manifest.posting_start == 0
    assert segments[0].manifest.posting_end == 3
    assert segments[0].read_cell(10) == (4, 5)
    assert segments[1].read_cell(30) == (9, 10, 11)


def test_query_segments_matches_union_of_requested_cells():
    segments = build_segments(
        [10, 20, 30],
        [0, 2, 3, 6],
        [4, 5, 8, 9, 10, 11],
        cells_per_segment=2,
    )

    assert query_segments(segments, [30, 10, 30]) == (4, 5, 9, 10, 11)
    assert query_segments(segments, [99]) == ()


def test_empty_input_builds_no_segments():
    assert build_segments([], [0], [], cells_per_segment=2) == ()
