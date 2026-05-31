import itertools
import sys
from collections.abc import Iterable, Sequence

from hamcrest import assert_that, equal_to

from countably import NumberSequence


def take(seq: Iterable[float], n: int) -> Sequence[float]:
    """Return the first ``n`` elements of ``seq`` as a list.

    Args:
        seq: The (possibly infinite) iterable to read from.
        n: How many leading elements to collect.

    Returns:
        The first ``n`` elements of ``seq``.
    """
    return list(itertools.islice(seq, n))


def as_seq(value: object) -> NumberSequence:
    """Narrow ``value`` to :class:`NumberSequence` for the type checker.

    Args:
        value: The object expected to be a :class:`NumberSequence`.

    Returns:
        ``value`` typed as a :class:`NumberSequence`.
    """
    assert isinstance(value, NumberSequence)
    return value


def assert_prefix(seq: Iterable[float], expected: Sequence[float]) -> None:
    """Assert that the first ``len(expected)`` elements of ``seq`` match.

    Args:
        seq: The sequence whose leading elements to check.
        expected: The values the prefix is expected to equal.
    """
    assert_that(take(seq, len(expected)), equal_to(list(expected)))


def assert_finite(seq: NumberSequence, expected: Sequence[float]) -> None:
    """Assert that ``seq`` is finite and equals ``expected`` exactly.

    Args:
        seq: The finite sequence to check.
        expected: The full contents ``seq`` is expected to have.
    """
    assert_that(len(seq), equal_to(len(expected)))
    assert_that(list(seq), equal_to(list(expected)))


def assert_infinite(seq: NumberSequence) -> None:
    """Assert that ``seq`` reports an infinite length.

    Args:
        seq: The sequence expected to be infinite.
    """
    assert_that(len(seq), equal_to(sys.maxsize))


def assert_length(seq: NumberSequence, n: int) -> None:
    """Assert that ``seq`` reports a finite length of ``n``.

    Args:
        seq: The sequence whose length to check.
        n: The expected length.
    """
    assert_that(len(seq), equal_to(n))


def assert_at(seq: NumberSequence, index: int, value: float) -> None:
    """Assert that the element of ``seq`` at ``index`` equals ``value``.

    Args:
        seq: The sequence to index.
        index: The position to read.
        value: The expected element at ``index``.
    """
    assert_that(seq[index], equal_to(value))
