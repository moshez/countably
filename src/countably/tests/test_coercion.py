"""Tests for automatic coercion of plain numbers into sequences."""

import unittest

from countably import constant, count

from ._seq import assert_at, assert_prefix


class TestCoercion(unittest.TestCase):
    """Plain numbers are coerced into constant sequences in operations."""

    def test_int_on_left_matches_explicit_constant(self) -> None:
        """A left-hand int coerces just like an explicit constant."""
        assert_prefix((3 + count()) == (constant(3) + count()), [True] * 10)

    def test_int_on_right_matches_explicit_constant(self) -> None:
        """A right-hand int coerces just like an explicit constant."""
        assert_prefix((count() + 3) == (count() + constant(3)), [True] * 10)

    def test_float_coerces(self) -> None:
        """A float operand is coerced into a constant."""
        assert_prefix(0.5 + count(), [0.5, 1.5, 2.5])

    def test_chained_coercion(self) -> None:
        """Coercion works through a chain of operations."""
        assert_prefix(100 - 10 * count(), [100, 90, 80, 70])

    def test_coerced_value_at_index(self) -> None:
        """A coerced expression indexes to the expected element."""
        assert_at(10 - count(), 3, 7)
