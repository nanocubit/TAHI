from tahi_x.reference import Archivist, ExactQuery


def test_archive_query_matches_bruteforce():
    objects = {10: (0.1, 0.1), 20: (0.4, 0.4), 30: (0.9, 0.9)}
    archivist = Archivist((0.0, 0.0), (1.0, 1.0), (4, 4))
    snapshot, directory, postings, canonical = archivist.build(objects)
    result = ExactQuery(snapshot, directory, postings, canonical).range((0.0, 0.0), (0.5, 0.5))
    assert result == [10, 20]


def test_sparse_directory_lookup_stats():
    objects = {1: (0.1, 0.1), 2: (0.9, 0.9)}
    archivist = Archivist((0.0, 0.0), (1.0, 1.0), (4, 4))
    snapshot, directory, postings, canonical = archivist.build(objects)
    engine = ExactQuery(snapshot, directory, postings, canonical)
    assert engine.range((0.0, 0.0), (0.2, 0.2)) == [1]
    assert engine.last_stats["retrieved_postings"] == 1
    assert engine.last_stats["exact_checks"] == 1


def test_query_outside_domain_is_empty():
    objects = {1: (0.2, 0.2)}
    archivist = Archivist((0.0, 0.0), (1.0, 1.0), (4, 4))
    snapshot, directory, postings, canonical = archivist.build(objects)
    assert ExactQuery(snapshot, directory, postings, canonical).range((2.0, 2.0), (3.0, 3.0)) == []


def test_postings_are_contiguous_and_deterministic():
    objects = {3: (0.2, 0.2), 1: (0.2, 0.2), 2: (0.8, 0.8)}
    archivist = Archivist((0.0, 0.0), (1.0, 1.0), (2, 2))
    _, directory, postings, _ = archivist.build(objects)
    assert directory.keys == (directory.keys[0], directory.keys[1])
    assert postings.object_ids == (1, 3, 2)
