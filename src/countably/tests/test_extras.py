import itertools
import math
import unittest
from typing import Iterable

from hamcrest import assert_that, equal_to

from countably import constant, count, maximum, minimum


def _take(seq: Iterable[float], n: int) -> list[float]:
    return list(itertools.islice(seq, n))


class TestComparison(unittest.TestCase):
    def test_lt(self) -> None:
        assert_that(_take(count() < 3, 5), equal_to([True, True, True, False, False]))

    def test_le(self) -> None:
        assert_that(_take(count() <= 3, 5), equal_to([True, True, True, True, False]))

    def test_gt(self) -> None:
        assert_that(_take(count() > 3, 5), equal_to([False, False, False, False, True]))

    def test_ge(self) -> None:
        assert_that(_take(count() >= 3, 5), equal_to([False, False, False, True, True]))

    def test_seq_against_seq(self) -> None:
        seq = count() < count() + 2
        assert_that(_take(seq, 3), equal_to([True, True, True]))


class TestRounding(unittest.TestCase):
    def test_floor(self) -> None:
        seq = math.floor(count() / 2)
        assert_that(_take(seq, 5), equal_to([0, 0, 1, 1, 2]))

    def test_ceil(self) -> None:
        seq = math.ceil(count() / 2)
        assert_that(_take(seq, 5), equal_to([0, 1, 1, 2, 2]))

    def test_trunc_negative_values(self) -> None:
        seq = math.trunc((count() - 4) / 2)
        assert_that(_take(seq, 5), equal_to([-2, -1, -1, 0, 0]))

    def test_round_default(self) -> None:
        seq = round(count() / 2)
        assert_that(_take(seq, 5), equal_to([0, 0, 1, 2, 2]))

    def test_round_with_ndigits(self) -> None:
        seq = round(count() / 3, 2)
        assert_that(_take(seq, 4), equal_to([0.0, 0.33, 0.67, 1.0]))


class TestMaxMin(unittest.TestCase):
    def test_maximum_seq_and_number(self) -> None:
        assert_that(_take(maximum(count(), 3), 6), equal_to([3, 3, 3, 3, 4, 5]))

    def test_minimum_seq_and_number(self) -> None:
        assert_that(_take(minimum(count(), 3), 6), equal_to([0, 1, 2, 3, 3, 3]))

    def test_maximum_two_seqs(self) -> None:
        seq = maximum(count(), constant(2))
        assert_that(_take(seq, 5), equal_to([2, 2, 2, 3, 4]))

    def test_minimum_two_seqs(self) -> None:
        seq = minimum(count(), constant(3))
        assert_that(_take(seq, 5), equal_to([0, 1, 2, 3, 3]))


class TestFibonacci(unittest.TestCase):
    def test_first_terms(self) -> None:
        phi = (1 + math.sqrt(5)) / 2
        sqrt5 = math.sqrt(5)
        fib = round(phi ** count() / sqrt5)
        assert_that(
            _take(fib, 12),
            equal_to([0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]),
        )
