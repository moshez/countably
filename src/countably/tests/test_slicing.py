"""Tests for lazy slicing and how slice lengths combine."""

import unittest

from hamcrest import assert_that, raises

from countably import constant, count

from ._seq import (
    as_seq as _seq,
    assert_finite,
    assert_infinite,
    assert_length,
    assert_prefix,
)


class TestInfiniteSlice(unittest.TestCase):
    """Slicing an infinite sequence without a stop stays infinite."""

    def test_default_slice(self) -> None:
        """The full slice reproduces the sequence."""
        seq = _seq(count()[:])
        assert_prefix(seq, [0, 1, 2, 3])
        assert_infinite(seq)

    def test_start_only(self) -> None:
        """A start-only slice drops the leading elements."""
        seq = _seq(count()[3:])
        assert_prefix(seq, [3, 4, 5, 6])
        assert_infinite(seq)

    def test_step_only(self) -> None:
        """A step-only slice keeps every nth element."""
        seq = _seq(count()[::2])
        assert_prefix(seq, [0, 2, 4, 6])
        assert_infinite(seq)

    def test_start_and_step(self) -> None:
        """A start-and-step slice combines both."""
        seq = _seq(count()[2::3])
        assert_prefix(seq, [2, 5, 8, 11])
        assert_infinite(seq)


class TestFiniteSlice(unittest.TestCase):
    """A bounded slice has a true, finite length."""

    def test_start_stop(self) -> None:
        """A start:stop slice yields the half-open range."""
        assert_finite(_seq(count()[2:7]), [2, 3, 4, 5, 6])

    def test_start_stop_step(self) -> None:
        """A start:stop:step slice steps within the range."""
        assert_finite(_seq(count()[2:10:3]), [2, 5, 8])

    def test_stop_smaller_than_start(self) -> None:
        """A stop before the start yields an empty sequence."""
        assert_finite(_seq(count()[5:3]), [])

    def test_stop_at_boundary(self) -> None:
        """A stop exactly at a step boundary excludes it."""
        assert_finite(_seq(count()[2:11:3]), [2, 5, 8])

    def test_stop_at_next_boundary(self) -> None:
        """A stop just past a step boundary includes it."""
        assert_finite(_seq(count()[2:12:3]), [2, 5, 8, 11])

    def test_finite_iter(self) -> None:
        """A finite slice iterates over its contents."""
        assert_finite(_seq(count()[0:3]), [0, 1, 2])


class TestSliceOfSlice(unittest.TestCase):
    """Slicing a slice composes the two slices lazily."""

    def test_finite_of_finite(self) -> None:
        """A finite slice of a finite slice is finite."""
        assert_finite(_seq(_seq(count()[2:20:3])[1:4]), [5, 8, 11])

    def test_infinite_of_infinite(self) -> None:
        """An infinite slice of an infinite slice stays infinite."""
        assert_prefix(_seq(_seq(count()[2::3])[1::2]), [5, 11, 17, 23])


class TestArithmeticBetweenSlices(unittest.TestCase):
    """Combining slices uses the shorter operand's length."""

    def test_finite_plus_finite_shortest_wins(self) -> None:
        """Adding two finite slices takes the shorter length."""
        assert_finite(_seq(count()[2:10]) + _seq(count()[3:8]), [5, 7, 9, 11, 13])

    def test_finite_plus_infinite_finite_wins(self) -> None:
        """Adding a finite slice to an infinite one is finite."""
        assert_finite(_seq(count()[0:4]) + count(), [0, 2, 4, 6])

    def test_infinite_plus_infinite_infinite(self) -> None:
        """Adding two infinite slices stays infinite."""
        seq = _seq(count()[::2]) + _seq(count()[::3])
        assert_infinite(seq)
        assert_prefix(seq, [0, 5, 10, 15])


class TestSliceErrors(unittest.TestCase):
    """Invalid slice bounds raise ValueError."""

    def test_zero_step_raises(self) -> None:
        """A zero step is rejected."""
        assert_that(lambda: count()[slice(0, 10, 0)], raises(ValueError))

    def test_negative_step_value_raises(self) -> None:
        """A negative step is rejected."""
        assert_that(lambda: count()[slice(None, None, -1)], raises(ValueError))

    def test_negative_start_raises(self) -> None:
        """A negative start is rejected."""
        assert_that(lambda: count()[slice(-1, None, None)], raises(ValueError))

    def test_negative_stop_raises(self) -> None:
        """A negative stop is rejected."""
        assert_that(lambda: count()[slice(0, -1, None)], raises(ValueError))


class TestSliceOfConstant(unittest.TestCase):
    """Slicing a constant preserves the constant value."""

    def test_infinite_slice(self) -> None:
        """An infinite slice of a constant is the same constant."""
        assert_prefix(_seq(constant(5)[2::3]), [5, 5, 5, 5])

    def test_finite_slice(self) -> None:
        """A finite slice of a constant repeats the value."""
        assert_finite(_seq(constant(5)[2:5]), [5, 5, 5])


class TestFiniteSliceLength(unittest.TestCase):
    """Slice length reporting for finite and infinite slices."""

    def test_finite_slice_real_len(self) -> None:
        """A bounded slice reports its real length."""
        assert_length(_seq(count()[2:10]), 8)

    def test_infinite_slice_maxsize_len(self) -> None:
        """An unbounded slice reports an infinite length."""
        assert_infinite(_seq(count()[2::3]))
