import random

from tahi_x.reference.segmented import SegmentedReferenceIndex


def _make_fixture(seed: int, cell_count: int):
    rng = random.Random(seed)
    cell_keys = list(range(100, 100 + cell_count))
    offsets = [0]
    object_ids = []
    next_id = 0
    for _ in cell_keys:
        postings = rng.randint(0, 8)
        ids = [next_id + i for i in range(postings)]
        object_ids.extend(ids)
        next_id += postings
        offsets.append(len(object_ids))
    return cell_keys, offsets, object_ids


def _reference_query(cell_keys, offsets, object_ids, wanted):
    positions = {key: index for index, key in enumerate(cell_keys)}
    result = set()
    for key in wanted:
        index = positions.get(key)
        if index is not None:
            result.update(object_ids[offsets[index]:offsets[index + 1]])
    return tuple(sorted(result))


def test_randomized_segmented_queries_match_reference_union():
    for seed in range(10):
        cell_keys, offsets, object_ids = _make_fixture(seed, cell_count=37)
        for cells_per_segment in (1, 2, 5, 16, 64):
            index = SegmentedReferenceIndex.build(
                cell_keys,
                offsets,
                object_ids,
                cells_per_segment=cells_per_segment,
            )
            rng = random.Random(seed + 1000)
            for _ in range(50):
                wanted = [rng.randrange(95, 145) for _ in range(rng.randint(0, 20))]
                assert index.query_cells(wanted) == _reference_query(
                    cell_keys, offsets, object_ids, wanted
                )
