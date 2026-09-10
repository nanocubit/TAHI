import random

from tahi_x.reference import Archivist, ExactQuery


def test_randomized_exact_oracle():
    for seed in range(10):
        rng = random.Random(seed)
        objects = {object_id: tuple(rng.random() for _ in range(5)) for object_id in range(3000)}
        archivist = Archivist((0.0,) * 5, (1.0,) * 5, (16,) * 5)
        snapshot, directory, postings, canonical = archivist.build(objects)
        engine = ExactQuery(snapshot, directory, postings, canonical)
        for _ in range(100):
            lo = tuple(rng.random() * 0.8 for _ in range(5))
            hi = tuple(min(1.0, value + rng.random() * 0.2) for value in lo)
            actual = engine.range(lo, hi)
            expected = sorted(object_id for object_id, point in objects.items() if all(low <= value <= high for value, low, high in zip(point, lo, hi)))
            assert actual == expected
