from tahi_x.reference.segmented import SegmentedReferenceIndex


def test_segmented_reference_index_queries_and_exposes_manifests():
    index = SegmentedReferenceIndex.build(
        [10, 20, 30],
        [0, 2, 3, 6],
        [4, 5, 8, 9, 10, 11],
        cells_per_segment=2,
    )

    assert index.query_cells([30, 10, 30]) == (4, 5, 9, 10, 11)
    manifests = index.manifests()
    assert len(manifests) == 2
    assert manifests[0]["format"] == "raw-v1"
    assert manifests[1]["cell_min"] == 30
