import itertools
import sys
import unittest
from typing import Iterable

from hamcrest import assert_that, equal_to, raises

from countably import NumberSequence, constant, count


def _take(seq: Iterable[float], n: int) -> list[float]:
    return list(itertools.islice(seq, n))


def _seq(value: object) -> NumberSequence:
    assert isinstance(value, NumberSequence)
    return value


class TestInfiniteSlice(unittest.TestCase):
    def test_default_slice(self) -> None:
        seq = _seq(count()[:])
        assert_that(_take(seq, 4), equal_to([0, 1, 2, 3]))
        assert_that(len(seq), equal_to(sys.maxsize))

    def test_start_only(self) -> None:
        seq = _seq(count()[3:])
        assert_that(_take(seq, 4), equal_to([3, 4, 5, 6]))
        assert_that(len(seq), equal_to(sys.maxsize))

    def test_step_only(self) -> None:
        seq = _seq(count()[::2])
        assert_that(_take(seq, 4), equal_to([0, 2, 4, 6]))
        assert_that(len(seq), equal_to(sys.maxsize))

    def test_start_and_step(self) -> None:
        seq = _seq(count()[2::3])
        assert_that(_take(seq, 4), equal_to([2, 5, 8, 11]))
        assert_that(len(seq), equal_to(sys.maxsize))


class TestFiniteSlice(unittest.TestCase):
    def test_start_stop(self) -> None:
        seq = _seq(count()[2:7])
        assert_that(len(seq), equal_to(5))
        assert_that(list(seq), equal_to([2, 3, 4, 5, 6]))

    def test_start_stop_step(self) -> None:
        seq = _seq(count()[2:10:3])
        assert_that(len(seq), equal_to(3))
        assert_that(list(seq), equal_to([2, 5, 8]))

    def test_stop_smaller_than_start(self) -> None:
        seq = _seq(count()[5:3])
        assert_that(len(seq), equal_to(0))
        assert_that(list(seq), equal_to([]))

    def test_stop_at_boundary(self) -> None:
        seq = _seq(count()[2:11:3])
        assert_that(len(seq), equal_to(3))
        assert_that(list(seq), equal_to([2, 5, 8]))

    def test_stop_at_next_boundary(self) -> None:
        seq = _seq(count()[2:12:3])
        assert_that(len(seq), equal_to(4))
        assert_that(list(seq), equal_to([2, 5, 8, 11]))

    def test_finite_iter(self) -> None:
        seq = _seq(count()[0:3])
        assert_that(list(seq), equal_to([0, 1, 2]))


class TestSliceOfSlice(unittest.TestCase):
    def test_finite_of_finite(self) -> None:
        seq = _seq(_seq(count()[2:20:3])[1:4])
        assert_that(list(seq), equal_to([5, 8, 11]))

    def test_infinite_of_infinite(self) -> None:
        seq = _seq(_seq(count()[2::3])[1::2])
        assert_that(_take(seq, 4), equal_to([5, 11, 17, 23]))


class TestArithmeticBetweenSlices(unittest.TestCase):
    def test_finite_plus_finite_shortest_wins(self) -> None:
        left = _seq(count()[2:10])
        right = _seq(count()[3:8])
        combined = left + right
        assert_that(len(combined), equal_to(5))
        assert_that(list(combined), equal_to([5, 7, 9, 11, 13]))

    def test_finite_plus_infinite_finite_wins(self) -> None:
        seq = _seq(count()[0:4]) + count()
        assert_that(len(seq), equal_to(4))
        assert_that(list(seq), equal_to([0, 2, 4, 6]))

    def test_infinite_plus_infinite_infinite(self) -> None:
        seq = _seq(count()[::2]) + _seq(count()[::3])
        assert_that(len(seq), equal_to(sys.maxsize))
        assert_that(_take(seq, 4), equal_to([0, 5, 10, 15]))


class TestSliceErrors(unittest.TestCase):
    def test_zero_step_raises(self) -> None:
        assert_that(lambda: count()[slice(0, 10, 0)], raises(ValueError))

    def test_negative_step_raises(self) -> None:
        assert_that(lambda: count()[slice(None, None, -1)], raises(ValueError))

    def test_negative_start_raises(self) -> None:
        assert_that(lambda: count()[slice(-1, None, None)], raises(ValueError))

    def test_negative_stop_raises(self) -> None:
        assert_that(lambda: count()[slice(0, -1, None)], raises(ValueError))


class TestSliceOfConstant(unittest.TestCase):
    def test_infinite_slice(self) -> None:
        seq = _seq(constant(5)[2::3])
        assert_that(_take(seq, 4), equal_to([5, 5, 5, 5]))

    def test_finite_slice(self) -> None:
        seq = _seq(constant(5)[2:5])
        assert_that(list(seq), equal_to([5, 5, 5]))


class TestFiniteSliceLength(unittest.TestCase):
    def test_finite_slice_real_len(self) -> None:
        seq = _seq(count()[2:10])
        assert_that(len(seq), equal_to(8))

    def test_infinite_slice_maxsize_len(self) -> None:
        seq = _seq(count()[2::3])
        assert_that(len(seq), equal_to(sys.maxsize))
