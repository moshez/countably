import itertools
from typing import Iterable

from countably import NumberSequence


def take(seq: Iterable[float], n: int) -> list[float]:
    return list(itertools.islice(seq, n))


def as_seq(value: object) -> NumberSequence:
    assert isinstance(value, NumberSequence)
    return value
