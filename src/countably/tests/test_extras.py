"""Tests for comparisons, rounding, max/min helpers, and Fibonacci."""

import math
import unittest

from countably import constant, count, maximum, minimum

from ._seq import assert_prefix


class TestComparison(unittest.TestCase):
    """Comparison operators produce element-wise boolean sequences."""

    def test_less_than(self) -> None:
        """``<`` compares each element against the bound."""
        assert_prefix(count() < 3, [True, True, True, False, False])

    def test_less_equal(self) -> None:
        """``<=`` includes the boundary element."""
        assert_prefix(count() <= 3, [True, True, True, True, False])

    def test_greater_than(self) -> None:
        """``>`` compares each element against the bound."""
        assert_prefix(count() > 3, [False, False, False, False, True])

    def test_greater_equal(self) -> None:
        """``>=`` includes the boundary element."""
        assert_prefix(count() >= 3, [False, False, False, True, True])

    def test_seq_against_seq(self) -> None:
        """Two sequences compare element-wise."""
        assert_prefix(count() < count() + 2, [True, True, True])


class TestRounding(unittest.TestCase):
    """Sequences cooperate with the standard rounding functions."""

    def test_floor(self) -> None:
        """``math.floor`` rounds each element down."""
        assert_prefix(math.floor(count() / 2), [0, 0, 1, 1, 2])

    def test_ceil(self) -> None:
        """``math.ceil`` rounds each element up."""
        assert_prefix(math.ceil(count() / 2), [0, 1, 1, 2, 2])

    def test_trunc_negative_values(self) -> None:
        """``math.trunc`` rounds toward zero."""
        assert_prefix(math.trunc((count() - 4) / 2), [-2, -1, -1, 0, 0])

    def test_round_default(self) -> None:
        """``round`` applies banker's rounding."""
        assert_prefix(round(count() / 2), [0, 0, 1, 2, 2])

    def test_round_with_ndigits(self) -> None:
        """``round`` honors a digit count."""
        assert_prefix(round(count() / 3, 2), [0.0, 0.33, 0.67, 1.0])


class TestMaxMin(unittest.TestCase):
    """The ``maximum`` and ``minimum`` helpers work element-wise."""

    def test_maximum_seq_and_number(self) -> None:
        """``maximum`` clamps a sequence from below by a number."""
        assert_prefix(maximum(count(), 3), [3, 3, 3, 3, 4, 5])

    def test_minimum_seq_and_number(self) -> None:
        """``minimum`` clamps a sequence from above by a number."""
        assert_prefix(minimum(count(), 3), [0, 1, 2, 3, 3, 3])

    def test_maximum_two_seqs(self) -> None:
        """``maximum`` takes the larger element of two sequences."""
        assert_prefix(maximum(count(), constant(2)), [2, 2, 2, 3, 4])

    def test_minimum_two_seqs(self) -> None:
        """``minimum`` takes the smaller element of two sequences."""
        assert_prefix(minimum(count(), constant(3)), [0, 1, 2, 3, 3])


class TestFibonacci(unittest.TestCase):
    """Binet's formula yields the Fibonacci sequence."""

    def test_first_terms(self) -> None:
        """Rounding Binet's formula reproduces the Fibonacci numbers."""
        phi = (1 + math.sqrt(5)) / 2
        sqrt5 = math.sqrt(5)
        fib = round(phi ** count() / sqrt5)
        assert_prefix(fib, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89])
