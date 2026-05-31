"""Tests for the primitive sequences and basic protocol behavior."""

import unittest

from hamcrest import assert_that, equal_to, raises

from countably import NumberSequence, constant, count

from ._seq import as_seq as _seq, assert_at, assert_infinite, assert_prefix


class TestConstant(unittest.TestCase):
    """``constant`` produces an infinite sequence of a single value."""

    def test_value_at_zero(self) -> None:
        """The first element is the constant value."""
        assert_at(constant(7), 0, 7)

    def test_value_at_large_index(self) -> None:
        """A far-off index still returns the constant value."""
        assert_at(constant(7), 10_000, 7)

    def test_is_sequence(self) -> None:
        """A constant satisfies the NumberSequence protocol."""
        assert_that(isinstance(constant(7), NumberSequence), equal_to(True))

    def test_length_is_maxsize(self) -> None:
        """A constant is infinite."""
        assert_infinite(constant(7))

    def test_iter(self) -> None:
        """Iterating a constant yields the value repeatedly."""
        assert_prefix(constant(7), [7, 7, 7, 7])


class TestCount(unittest.TestCase):
    """``count`` produces the infinite sequence of natural numbers."""

    def test_value_at_zero(self) -> None:
        """Counting starts at zero."""
        assert_at(count(), 0, 0)

    def test_value_at_index(self) -> None:
        """Element ``n`` of count is ``n``."""
        assert_at(count(), 42, 42)

    def test_length_is_maxsize(self) -> None:
        """Counting is infinite."""
        assert_infinite(count())

    def test_is_sequence(self) -> None:
        """A count satisfies the NumberSequence protocol."""
        assert_that(isinstance(count(), NumberSequence), equal_to(True))

    def test_iter(self) -> None:
        """Iterating count yields successive naturals."""
        assert_prefix(count(), [0, 1, 2, 3, 4])


class TestBoolFails(unittest.TestCase):
    """Sequences have no defined truth value."""

    def test_bool_constant_raises(self) -> None:
        """``bool`` of a constant raises TypeError."""
        assert_that(lambda: bool(constant(7)), raises(TypeError))

    def test_bool_count_raises(self) -> None:
        """``bool`` of a count raises TypeError."""
        assert_that(lambda: bool(count()), raises(TypeError))

    def test_bool_expression_raises(self) -> None:
        """``bool`` of a derived sequence raises TypeError."""
        assert_that(lambda: bool(3 + count()), raises(TypeError))


class TestStr(unittest.TestCase):
    """``str`` renders a readable preview of a sequence."""

    def test_infinite_count(self) -> None:
        """An infinite count is rendered with an ellipsis tail."""
        assert_that(str(count()), equal_to("[0, 1, 2, 3, 4, ....]"))

    def test_infinite_constant(self) -> None:
        """An infinite constant is rendered with an ellipsis tail."""
        assert_that(str(constant(7)), equal_to("[7, 7, 7, 7, 7, ....]"))

    def test_finite_slice(self) -> None:
        """A finite slice is rendered as its full contents."""
        assert_that(str(_seq(count()[2:5])), equal_to("[2, 3, 4]"))

    def test_empty_finite(self) -> None:
        """An empty finite slice is rendered as an empty list."""
        assert_that(str(_seq(count()[5:3])), equal_to("[]"))


class TestIndexBounds(unittest.TestCase):
    """Indexing respects sequence bounds and finiteness."""

    def test_negative_index_on_infinite_raises(self) -> None:
        """A negative index into an infinite sequence raises IndexError."""
        assert_that(lambda: count()[-1], raises(IndexError))

    def test_out_of_range_finite_raises(self) -> None:
        """Indexing past the end of a finite slice raises IndexError."""
        seq = _seq(count()[0:3])
        assert_that(lambda: seq[3], raises(IndexError))

    def test_finite_negative_index_works(self) -> None:
        """A negative index counts back from the end of a finite slice."""
        assert_at(_seq(count()[2:10]), -1, 9)

    def test_finite_negative_out_of_range_raises(self) -> None:
        """A too-negative index into a finite slice raises IndexError."""
        seq = _seq(count()[2:5])
        assert_that(lambda: seq[-4], raises(IndexError))
